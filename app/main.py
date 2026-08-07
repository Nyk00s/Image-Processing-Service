from fastapi import FastAPI
from app.dependencies import get_settings
from contextlib import asynccontextmanager
from app.routers import auth, pictures, tasks
from app.storage import build_s3_client, ensure_bucket
from app.exception_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    s3 = build_s3_client(settings, public=False)
    ensure_bucket(s3, settings.s3_bucket)
    yield

app = FastAPI(title="Image Processing Service", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(auth.router)
app.include_router(pictures.router)
app.include_router(tasks.router)
