from fastapi import FastAPI
from api import router as api_router

app = FastAPI()

# Подключаем роутер
app.include_router(api_router)
