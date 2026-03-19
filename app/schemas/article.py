from pydantic import BaseModel


class ArticleResponse(BaseModel):
    article_id: int
    title: str | None
    sub_title: str | None
    writers: str | None
    service_daytime: str | None
    reg_dt: str | None
    mod_dt: str | None
    pub_date: str | None
    pub_section: str | None
    pub_page: str | None
    pub_div: str | None
    lang: str | None
    main_category: str | None
    body: str | None
    summary: str | None
    article_url: str | None
    keywords: str | None
    keyword_list: str | None
    like_count: int | None
    reply_count: int | None
    images: str | None
    categories: str | None
    comments: str | None

    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    articles: list[ArticleResponse]


class ConvertRequest(BaseModel):
    article_url: str


class ConvertResponse(BaseModel):
    article_url: str
    original_body: str
    converted_text: str
