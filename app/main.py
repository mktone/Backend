from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.databases.news_session import create_tables
    from app.core.config import settings

    create_tables()
    print(f"SIGN DB: {settings.SIGN_DB_HOST}:{settings.SIGN_DB_PORT}/{settings.SIGN_DB_NAME}", flush=True)

    yield


app = FastAPI(
    lifespan=lifespan,
    title="수어로 보는 뉴스 API",
    description="청각장애인을 위한 수어 뉴스 서비스 백엔드 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import articles, convert, sign
app.include_router(articles.router, prefix="/api/v1")
app.include_router(convert.router, prefix="/api/v1")
app.include_router(sign.router, prefix="/api/v1")


@app.get(
    "/health",
    tags=["Health"],
    summary="서버 상태 확인",
    description="서버가 정상 동작 중인지 확인합니다",
    responses={200: {"description": "서버 정상 동작 중"}},
)
def health_check():
    return {"status": "ok", "message": "서버가 정상 동작 중입니다"}
