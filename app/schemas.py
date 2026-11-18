from pydantic import BaseModel


class IngestRequest(BaseModel):
    url: str


class IngestResponse(BaseModel):
    video_id: str
    chunks_stored: int
    cached: bool = False


class AskRequest(BaseModel):
    video_id: str
    question: str


class Source(BaseModel):
    timestamp: str   # "14:32"
    url: str         # clickable deep link
    text: str        # the chunk text used


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]