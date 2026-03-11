from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.schemas.article import ConvertRequest, ConvertResponse
from app.services.article_service import get_article_by_url
from app.services.claude_service import convert_to_sign_language

router = APIRouter(tags=["Convert"])


@router.post(
    "/convert",
    response_model=ConvertResponse,
    summary="수어 변환",
    description="article_url로 기사 본문을 조회하고 한국수어 문법에 맞게 변환합니다",
    responses={
        200: {"description": "수어 변환 성공"},
        404: {"description": "기사를 찾을 수 없음"},
        422: {"description": "파라미터 오류"},
        500: {"description": "서버 오류"},
    },
)
def convert_article(request: ConvertRequest, db: Session = Depends(get_news_db)):
    article = get_article_by_url(db, request.article_url)
    converted_text = convert_to_sign_language(article.body)
    return ConvertResponse(
        article_url=request.article_url,
        original_body=article.body,
        converted_text=converted_text,
    )
