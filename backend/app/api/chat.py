from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
)

from app.core.rate_limit import limiter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import (
    generate_chat_response,
    ChatServiceError,
)


router = APIRouter(
    prefix="/chat",
    tags=["AI Portfolio Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
@limiter.limit("10/minute")
async def chat(
    payload: ChatRequest,
    request: Request,
    response: Response,
):
    try:
        result = await generate_chat_response(
            message=payload.message.strip(),
            history=payload.history,
        )

        return ChatResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
        )

    except ChatServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )