from typing import Literal

from pydantic import Field

from app.schemas.profile import StrictSchema


class ChatMessage(StrictSchema):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(StrictSchema):
    message: str = Field(min_length=1, max_length=2000)

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=8,
    )


class ChatResponse(StrictSchema):
    success: bool = True
    answer: str
    sources: list[str] = Field(default_factory=list)