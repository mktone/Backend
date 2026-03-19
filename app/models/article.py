from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from app.databases.news_session import Base


class Article(Base):
    __tablename__ = "articles"

    article_id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=True)
    sub_title = Column(String(500), nullable=True)
    writers = Column(String(500), nullable=True)
    service_daytime = Column(String(50), nullable=True)
    reg_dt = Column(String(50), nullable=True)
    mod_dt = Column(String(50), nullable=True)
    pub_date = Column(String(50), nullable=True)
    pub_section = Column(String(100), nullable=True)
    pub_page = Column(String(50), nullable=True)
    pub_div = Column(String(50), nullable=True)
    lang = Column(String(10), nullable=True)
    main_category = Column(String(50), nullable=True)
    body = Column(MEDIUMTEXT, nullable=True)
    summary = Column(MEDIUMTEXT, nullable=True)
    article_url = Column(String(500), nullable=True, unique=True)
    keywords = Column(String(500), nullable=True)
    keyword_list = Column(String(500), nullable=True)
    like_count = Column(Integer, nullable=True)
    reply_count = Column(Integer, nullable=True)
    images = Column(MEDIUMTEXT, nullable=True)       # JSON string
    categories = Column(MEDIUMTEXT, nullable=True)   # JSON string
    comments = Column(MEDIUMTEXT, nullable=True)     # JSON string
