from sqlalchemy import Column, Integer, String, Float

from app.databases.sign_session import SignBase


class SignFingerspelling(SignBase):
    __tablename__ = "sign_fingerspelling"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    jamo         = Column(String(10),  nullable=False, index=True)  # 자모 (예: ㄱ, ㄴ, ㅏ)
    duration_sec = Column(Float,       nullable=False)              # 진행 시간 (초)
    frames       = Column(Integer,     nullable=False)              # 프레임 수
    fps          = Column(Float,       nullable=False)              # 초당 프레임 수
    npy_path     = Column(String(500), nullable=False)              # npy 파일 경로 (shape: frames, 543, 3)