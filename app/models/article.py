from sqlalchemy import Column, Integer, String, Text

from app.databases.news_session import Base


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=True)
    writers = Column(String(200), nullable=True)
    service_daytime = Column(String(50), nullable=True)
    main_category = Column(String(50), nullable=True)
    body = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    article_url = Column(String(500), nullable=True, unique=True)
    keyword_list = Column(String(500), nullable=True)
    like_count = Column(Integer, nullable=True)
    reply_count = Column(Integer, nullable=True)
