from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.schemas.article import ArticleResponse
from app.services.article_service import get_article_by_url

router = APIRouter()


@router.get("/articles", response_model=ArticleResponse)
def get_article(url: str, db: Session = Depends(get_news_db)):
    return get_article_by_url(db, url)
