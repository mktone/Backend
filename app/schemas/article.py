from pydantic import BaseModel


class ArticleResponse(BaseModel):
    article_id: int
    title: str | None
    writers: str | None
    service_daytime: str | None
    main_category: str | None
    body: str | None
    summary: str | None
    article_url: str | None
    keyword_list: str | None
    like_count: int | None
    reply_count: int | None

    class Config:
        from_attributes = True
