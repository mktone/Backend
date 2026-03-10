from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.schemas.article import ArticleResponse
from app.services.article_service import get_article_by_url

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
