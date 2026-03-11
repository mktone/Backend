from sqlalchemy.orm import Session

from app.models.article import Article


def get_article_by_url(db: Session, article_url: str):
    return db.query(Article).filter(Article.article_url == article_url).first()
