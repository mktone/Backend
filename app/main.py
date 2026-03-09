from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.databases.news_session import create_tables
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 추가 예정
# from app.routers import articles, convert
# app.include_router(articles.router)
# app.include_router(convert.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
