import logging
import pickle
from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
from sqlalchemy.orm import Session
from database.database import get_session
from models.MLTask import MLtaskORM
from schemas.MLTask import MLResultCreate, MLResultRead, MLTaskCreate, MLTaskRead, PredictionInput
from services.crud import MLTask as MLTaskServices
from services.crud import user as UserServices
from typing import Dict
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from catboost import CatBoostClassifier
from auth.authenticate import authenticate_cookie

task_router = APIRouter(tags=['task'], prefix='/task')
result_router = APIRouter(tags=['result'], prefix='/result')
templates = Jinja2Templates(directory="view")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


@task_router.get("/predict", response_class=HTMLResponse)
async def get_predict(request: Request, user: str = Depends(authenticate_cookie)):
    context = {
        "user": user,
        "request": request
    }
    return templates.TemplateResponse("predict.html", context)



# Маршрут для POST-запроса с использованием response_model
@task_router.post("/predict", response_model=MLResultCreate, response_class=HTMLResponse)
async def post_predict(
    request: Request,
    country: str = Form(...),
    currency: str = Form(...),
    prelaunch_activated: bool = Form(...),
    staff_pick: bool = Form(...),
    static_usd_rate: float = Form(...),
    fx_rate: float = Form(...),
    created_at: str = Form(...),
    launched_at: str = Form(...),
    deadline: str = Form(...),
    name: str = Form(...),
    blurb: str = Form(...),
    usd_goal: float = Form(...),
    name_city: str = Form(...),
    region: str = Form(...),
    type: str = Form(...),
    ppohasaction: str = Form(...),
    analytics_name: str = Form(...),
    position: int = Form(...),
    parent_name: str = Form(...),
    is_not_first_project: bool = Form(...),
    has_video: bool = Form(...)
):
    # Собираем данные в словарь
    input_data = {
        'country': country,
        'currency': currency,
        'prelaunch_activated': prelaunch_activated,
        'staff_pick': staff_pick,
        'static_usd_rate': static_usd_rate,
        'fx_rate': fx_rate,
        'created_at': created_at,
        'launched_at': launched_at,
        'deadline': deadline,
        'name': name,
        'blurb': blurb,
        'usd_goal': usd_goal,
        'name_city': name_city,
        'region': region,
        'type': type,
        'ppohasaction': ppohasaction,
        'analytics_name': analytics_name,
        'position': position,
        'parent_name': parent_name,
        'is_not_first_project': is_not_first_project,
        'has_video': has_video
    }
    preprocess_data = preprocess_input(input_data)
    logging.info(f"Preprocessed data: {preprocess_data}")

    if not isinstance(preprocess_data, pd.DataFrame):
        raise HTTPException(status_code=400, detail="Preprocessed data is not a DataFrame")

    prediction = predict(preprocess_data)
    logging.info(f"Prediction: {prediction}")

    return templates.TemplateResponse("predict.html", {"request": request, "prediction": prediction})