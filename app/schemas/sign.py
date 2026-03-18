from pydantic import BaseModel


class SignRequest(BaseModel):
    text: str


class SignSegment(BaseModel):
    word: str
    type: str        # "word" | "fingerspelling"
    fps: float
    frames: list[list[list[float]]]


class SignResponse(BaseModel):
    segments: list[SignSegment]
