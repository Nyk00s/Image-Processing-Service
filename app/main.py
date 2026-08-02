from fastapi import FastAPI
from app.dependencies import get_settings
from contextlib import asynccontextmanager
from app.routers import auth, pictures, tasks
from app.storage import build_s3_client, ensure_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    s3 = build_s3_client(settings)
    ensure_bucket(s3, settings.s3_bucket)
    yield

app = FastAPI(title="Image Processing Service", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(pictures.router)
app.include_router(tasks.router)
