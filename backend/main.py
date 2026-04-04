"""SupportIQ Chatbot — FastAPI entry point."""

import logging
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run as agent_run

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SupportIQ Chatbot API starting up")
    yield
    logger.info("SupportIQ Chatbot API shutting down")


# ---------------------------------------------------------------------------
# App + CORS
# ---------------------------------------------------------------------------

app = FastAPI(title="SupportIQ Chatbot API", version="1.0.0", lifespan=lifespan)

_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://support-iq.com.au,https://supportiq.com.au,http://localhost:3000,http://127.0.0.1:5500",
)
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class HistoryMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = []
    user: str = "User"


class ChatResponse(BaseModel):
    reply: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health() -> dict:
    """Liveness probe used by Cloud Run."""
    return {"status": "ok", "service": "supportiq-chatbot"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint — delegates to the Gemini agentic orchestrator."""
    logger.info(
        "Incoming message | user=%s | message_length=%d",
        request.user,
        len(request.message),
    )

    start = time.monotonic()
    try:
        history_dicts = [m.model_dump() for m in request.history]
        reply = await agent_run(request.message, history_dicts, request.user)
    except Exception:
        logger.exception("Orchestrator error for user=%s", request.user)
        reply = (
            "I'm having trouble right now. Please try again or book a demo at "
            "https://calendly.com/matthew-support-iq/30min"
        )

    elapsed_ms = int((time.monotonic() - start) * 1000)
    logger.info(
        "Reply sent | user=%s | reply_length=%d | latency_ms=%d",
        request.user,
        len(reply),
        elapsed_ms,
    )

    return ChatResponse(reply=reply)
