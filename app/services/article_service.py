from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.article import get_article_by_url as repo_get_article_by_url


def get_article_by_url(db: Session, article_url: str):
    article = repo_get_article_by_url(db, article_url)
    if not article:
        raise HTTPException(status_code=404, detail="기사를 찾을 수 없습니다.")
    return article
