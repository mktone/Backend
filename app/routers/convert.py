import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.news_session import get_news_db
from app.databases.sign_session import get_sign_db
from app.schemas.article import ConvertRequest, ConvertResponse
from app.services.article_service import get_article_by_url
from app.services.claude_service import convert_to_sign_language
from app.services.morpheme_service import match_sign_words, postprocess_converted_text, preprocess_remove_particles
from app.services.sign_service import get_available_sign_words

router = APIRouter(tags=["Convert"])


@router.post(
    "/convert",
    response_model=ConvertResponse,
    summary="수어 변환",
    description="article_url로 기사 본문을 조회하고 한국수어 문법에 맞게 변환합니다. sign_db 단어 목록을 참조하며, 없는 단어는 [지문자: 단어] 형식으로 표시됩니다.",
    responses={
        200: {"description": "수어 변환 성공"},
        404: {"description": "기사를 찾을 수 없음"},
        422: {"description": "파라미터 오류"},
        500: {"description": "서버 오류"},
    },
)
async def convert_article(
    request: ConvertRequest,
    news_db: Session = Depends(get_news_db),
    sign_db: Session = Depends(get_sign_db),
):
    article = get_article_by_url(news_db, request.article_url)
    sign_words = get_available_sign_words(sign_db)
    preprocessed_body = preprocess_remove_particles(article.body)
    available, unavailable, replacements = match_sign_words(preprocessed_body, sign_words)
    paragraphs = [p for p in preprocessed_body.split("\n") if p.strip()]
    converted_parts = await asyncio.gather(*[
        convert_to_sign_language(p, sign_words, available, unavailable, replacements)
        for p in paragraphs
    ])
    converted_text = "\n".join(converted_parts)
    converted_text = postprocess_converted_text(converted_text, sign_words)
    return ConvertResponse(
        article_url=request.article_url,
        original_body=article.body,
        converted_text=converted_text,
    )
