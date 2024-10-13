import os
from typing import Dict
from fastapi import Depends
import pika
import json
import pickle
import pandas as pd
from requests import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

from database.database import get_session
from routes.MLTask import MLTaskServices
from models.MLTask import MLResult


def categorize_goal(goal):
    categories = [
        (0, 500, 'simple project'),
        (500, 1000, 'low'),
        (1000, 1500, 'low2'),
        (1500, 2000, 'low3'),
        (2000, 2500, 'big low'),
        (2500, 3000, 'basic project'),
        (3000, 4000, 'basic project 2'),
        (4000, 5000, 'basic project 3'),
        (5000, 7500, 'serious'),
        (7500, 8750, 'project'),
        (8750, 10000, 'project 2'),
        (10000, 15000, 'big_project'),
        (15000, 20000, 'gigant project'),
        (20000, 25000, 'gigant project 2'),
        (25000, 50000, 'very gigant project'),
        (50000, 100000, 'big startup'),
        (100000, float('inf'), 'very expensive')
    ]
    for lower, upper, category in categories:
        if lower <= goal < upper:
            return category


def get_vader_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score['compound']  


def preprocess_input(data: Dict):
    for col in ['created_at', 'launched_at', 'deadline']:
        data[col] = pd.to_datetime(data[col], format='%Y-%m-%d')

    data['days_beetwen_created_launched'] = (data['launched_at'] - data['created_at']).days
    data['days_beetwen_created_deadline'] = (data['deadline'] - data['created_at']).days
    data['days_between_launched_deadline'] = (data['deadline'] - data['launched_at']).days
    data['create_day'], data['launch_day'] = data['created_at'].weekday(), data['launched_at'].weekday()
    data['deadline_day'] = data['deadline'].weekday()
    data['create_month'] = data['created_at'].month
    data['launch_month'] = data['launched_at'].month
    data['deadline_month'] = data['deadline'].month
    data['blurb_length'] = len(data['blurb'])
    data['word_count'] = len(data['blurb'].split())
    tfidf = TfidfVectorizer()
    tfidf_data = tfidf.fit_transform([data['name']])
    data['TotalTfId_name'] = tfidf_data.sum(axis=1).item() 
    data['MaxTfIdf_name'] = tfidf_data.max(axis=1).toarray().flatten()[0]
    data['MeanTfIdf_name'] = tfidf_data.mean(axis=1).item()
    tfidf_blurb = tfidf.fit_transform([data['blurb']])
    data['TotalTfId_blurb'] = tfidf_blurb.sum(axis=1).item()
    data['MaxTfIdf_blurb'] = tfidf_blurb.max(axis=1).toarray().flatten()[0]
    data['MeanTfIdf_blurb'] = tfidf_blurb.mean(axis=1).item()
    data['goal_category'] = categorize_goal(data['usd_goal'])
    data['sentiment_score_blurb'] = get_vader_sentiment(data['blurb'])
    data['sentiment_score_name'] = get_vader_sentiment(data['name'])
    keys_to_remove = ['blurb', 'name', 'created_at','launched_at', 'deadline']
    analytics_df = pd.read_json('output_analytics.json')
    parent_df = pd.read_json('output_parent.json')
    matching_rows = parent_df[parent_df['parent_name'] == data['parent_name']]
    matching_analytics_rows = analytics_df[analytics_df['analytics_name'] == data['analytics_name']]
    data['avg_goal_parent_category'] = matching_rows['avg_goal_parent_category'].values[0]
    data['avg_backers_parent_name_2'] = matching_rows['avg_backers_parent_name_2'].values[0]
    data['avg_backers_parent_name'] = matching_rows['avg_backers_parent_name'].values[0]
    data['goal_to_median_ratio'] = (data['usd_goal'] / matching_rows['usd_goal']).values[0]
    data['usd_goal_per_day'] = data['usd_goal'] / data['days_between_launched_deadline']
    data['avg_backers_analytics_name'] = matching_analytics_rows['avg_backers_analytics_name'].values[0]
    data['avg_backers_analytics_name_2'] = matching_analytics_rows['avg_backers_analytics_name_2'].values[0]
    data['avg_goal_analytics_category'] = matching_analytics_rows['avg_goal_analytics_category'].values[0]
    for key in keys_to_remove:
        data.pop(key, None)
    model_order = ['country', 'currency', 'prelaunch_activated', 'staff_pick',
            'static_usd_rate', 'fx_rate', 'days_beetwen_created_launched',
            'days_beetwen_created_deadline', 'days_between_launched_deadline',
            'create_day', 'launch_day', 'deadline_day', 'create_month',
            'launch_month', 'deadline_month', 'blurb_length', 'word_count',
            'usd_goal', 'goal_category', 'TotalTfId_name', 'MaxTfIdf_name',
            'MeanTfIdf_name', 'TotalTfId_blurb', 'MaxTfIdf_blurb',
            'MeanTfIdf_blurb', 'sentiment_score_blurb', 'sentiment_score_name',
            'name_city', 'region', 'type', 'ppoHasAction', 'analytics_name',
            'position', 'parent_name', 'goal_to_median_ratio', 'usd_goal_per_day',
            'has_video', 'avg_goal_parent_category', 'avg_goal_analytics_category',
            'avg_backers_analytics_name_2', 'avg_backers_parent_name_2',
            'avg_backers_analytics_name', 'avg_backers_parent_name',
            'is_not_first_project']
    df = pd.DataFrame([data])
    df = df.reindex(columns=model_order)
    return df


def predict(df:  pd.DataFrame):
    with open("best_model.pkl", "rb") as f:
        model = pickle.load(f)
    prediction = model.predict(df)
    return prediction[0]


def callback(ch, method, properties, body):
    message = json.loads(body)
    user_id = message['user_id']
    input_data = message['input_data']
    ml_task_id = message['ml_task_id']
    preprocess_data = preprocess_input(input_data)

    prediction = predict(preprocess_data)

    ml_result = MLResult(
        ml_task_id=ml_task_id,
        predict=int(prediction)
    )
    db: Session = next(get_session())
    try:
        MLTaskServices.create_result(ml_result, db)

        print(f"Processed prediction for user_id: {user_id}, prediction: {prediction}")
    except Exception as e:
        print(f"Error processing message for user_id {user_id}: {str(e)}")

    finally:
        db.close()


def main():
    connection_params = pika.ConnectionParameters(
        host='rabbitmq', 
        port=5672,          
        virtual_host='/',  
        credentials=pika.PlainCredentials(
            username=os.getenv('RABBITMQ_USER'),
            password=os.getenv('RABBITMQ_PASS')   
        )
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='prediction_queue', durable=True)

    channel.basic_consume(queue='prediction_queue', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
