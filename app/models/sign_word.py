from sqlalchemy import Column, Integer, String, Float

from app.databases.sign_session import SignBase


class SignWord(SignBase):
    __tablename__ = "sign_words"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    word         = Column(String(100), nullable=False, index=True)  # 단어명 (예: 약효)
    word_num     = Column(String(20),  nullable=False)              # WORD 번호 (예: WORD2145)
    signer       = Column(String(20),  nullable=False)              # 화자 ID (예: REAL01)
    direction    = Column(String(5),   nullable=False)              # 촬영 방향 (D/F/L/R/U)
    start        = Column(Float,       nullable=False)              # 수어 시작 시각 (초)
    end          = Column(Float,       nullable=False)              # 수어 종료 시각 (초)
    duration_sec = Column(Float,       nullable=False)              # 수어 진행 시간 (초)
    frames       = Column(Integer,     nullable=False)              # 프레임 수
    fps          = Column(Float,       nullable=False)              # 초당 프레임 수
    npy_path     = Column(String(500), nullable=False)              # npy 파일 경로
