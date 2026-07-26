from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Image Processing Service")

app.include_router(auth.router)
