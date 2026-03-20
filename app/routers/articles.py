from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.schemas.article import ArticleListResponse, ArticleResponse, SummarizeRequest, SummarizeResponse
from app.services.article_service import get_article_by_url, get_article_list
from app.services.summary_service import summarize_article

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
    description="최신순으로 기사 목록을 조회합니다. 기본 9개",
    responses={
        200: {"description": "기사 목록 조회 성공"},
        500: {"description": "서버 오류"},
    },
)
def get_article_list_api(limit: int = 9, db: Session = Depends(get_news_db)):
    articles = get_article_list(db, limit)
    return ArticleListResponse(articles=articles)


@router.post(
    "/articles/summarize",
    response_model=SummarizeResponse,
    summary="기사 요약",
    description="article_url로 기사 본문을 Claude API로 4~5줄 요약합니다",
    responses={
        200: {"description": "요약 성공"},
        404: {"description": "기사를 찾을 수 없음"},
        500: {"description": "서버 오류"},
    },
)
async def summarize_article_api(request: SummarizeRequest, db: Session = Depends(get_news_db)):
    article = get_article_by_url(db, request.article_url)
    summary = await summarize_article(article.body)
    return SummarizeResponse(article_url=request.article_url, summary=summary)
