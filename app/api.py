from fastapi import FastAPI
from routes.balance import balance_route
from routes.transaction import transactions_route
from routes.user import user_route
from routes.MLTask import task_router
from routes.model import model_route
from routes.overview import overview_route
from database.database import init_db
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.include_router(user_route)
app.include_router(balance_route)
app.include_router(transactions_route)
app.include_router(user_route)
app.include_router(task_router)
app.include_router(model_route)
app.include_router(overview_route)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Либо укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)
