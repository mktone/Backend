from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.schemas.article import ArticleListResponse, ArticleResponse
from app.services.article_service import get_article_by_url, get_article_list

router = APIRouter(tags=["Articles"])


@router.get(
    "/articles",
    response_model=ArticleResponse,
    summary="기사 조회",
    description="article_url로 기사 정보를 조회합니다",
    responses={
        200: {"description": "기사 조회 성공"},
        404: {"description": "기사를 찾을 수 없음"},
        422: {"description": "파라미터 오류"},
        500: {"description": "서버 오류"},
    },
)
def get_article(url: str, db: Session = Depends(get_news_db)):
    return get_article_by_url(db, url)


@router.get(
    "/articles/list",
    response_model=ArticleListResponse,
    summary="기사 목록 조회",
    description="최신순으로 기사 목록을 조회합니다. 기본 10개",
    responses={
        200: {"description": "기사 목록 조회 성공"},
        500: {"description": "서버 오류"},
    },
)
def get_article_list_api(limit: int = 9, db: Session = Depends(get_news_db)):
    articles = get_article_list(db, limit)
    return ArticleListResponse(articles=articles)
