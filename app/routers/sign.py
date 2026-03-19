from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.databases.sign_session import get_sign_db
from app.schemas.sign import SignRequest, SignResponse
from app.services.sign_service import get_sign_segments

router = APIRouter(tags=["Sign"])


@router.post(
    "/sign",
    response_model=SignResponse,
    summary="수어 세그먼트 반환",
    description="변환된 수어 텍스트를 받아 단어/지문자별 키포인트 프레임을 반환합니다.",
    responses={
        200: {"description": "수어 세그먼트 반환 성공"},
        422: {"description": "파라미터 오류"},
        500: {"description": "서버 오류"},
    },
)
def get_sign(
    request: SignRequest,
    sign_db: Session = Depends(get_sign_db),
):
    segments = get_sign_segments(sign_db, request.text)
    return SignResponse(segments=segments)
