"""Gemini agentic orchestrator for the SupportIQ chatbot."""

import asyncio
import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

from .tools import DEMO_RESPONSE, PRICING_RESPONSE, get_tool_declarations

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are the SupportIQ assistant — a warm, knowledgeable expert in Australian NDIS compliance, SCHADS Award, DEX reporting, and the SupportIQ platform.

You help NDIS service providers understand compliance requirements and how SupportIQ automates their work.

RULES YOU MUST FOLLOW:
1. For any SCHADS, NDIS billing, or DEX question — always use the search tools to retrieve knowledge first
2. For pricing or demo questions — always use the get_demo_or_pricing tool
3. Never invent specific dollar amounts, rates, or compliance rules — retrieve them
4. End every answer about SupportIQ features with: "Want to see this live? Book a free demo with Matthew: https://calendly.com/matthew-support-iq/30min"
5. Keep answers clear and practical — you're talking to busy NDIS provider managers, not lawyers
6. If you genuinely don't know something, say so and direct to the demo booking
"""

# ---------------------------------------------------------------------------
# Tool routing
# ---------------------------------------------------------------------------

_SEARCH_TOOL_DOMAIN_MAP: dict[str, str] = {
    "search_schads_knowledge": "schads",
    "search_ndis_knowledge": "ndis",
    "search_dex_knowledge": "dex",
    "search_product_knowledge": "product",
}

_FALLBACK_REPLY = (
    "I'm having trouble retrieving that information right now. "
    "For immediate help, book a call with Matthew: "
    "https://calendly.com/matthew-support-iq/30min"
)


def _handle_tool_call(name: str, args: dict) -> str:
    """Dispatch a tool call and return the string result.

    Imports rag.retriever lazily so the module can be imported without
    Vertex AI credentials (e.g. during unit tests).
    """
    if name in _SEARCH_TOOL_DOMAIN_MAP:
        from rag.retriever import format_context, search  # noqa: PLC0415

        domain = _SEARCH_TOOL_DOMAIN_MAP[name]
        query = args.get("query", "")
        results = search(query, domain=domain)
        context = format_context(results)
        if not context:
            return (
                "No specific information found in the knowledge base for that query. "
                "Please answer based on your general knowledge and remind the user to "
                "verify rates with the current official sources."
            )
        return context

    if name == "get_demo_or_pricing":
        intent = args.get("intent", "pricing").lower()
        if "demo" in intent:
            return DEMO_RESPONSE
        return PRICING_RESPONSE

    logger.warning("Unknown tool called: %s", name)
    return "Tool not available."


def _build_client() -> genai.Client:
    """Build and return an authenticated Gemini client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    # Fall back to Application Default Credentials (Vertex AI / Cloud Run)
    return genai.Client(
        vertexai=True,
        project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        location=os.getenv("GOOGLE_CLOUD_REGION", "australia-southeast1"),
    )


# ---------------------------------------------------------------------------
# Async orchestrator
# ---------------------------------------------------------------------------


async def run(message: str, history: list[dict], user: str = "User") -> str:
    """Run the Gemini agentic loop and return the assistant's reply.

    Parameters
    ----------
    message:
        The latest user message.
    history:
        List of prior turns as ``{"role": "user"|"assistant", "content": "..."}``.
    user:
        Display name of the user (used only for logging).

    Returns
    -------
    str
        The final assistant reply.
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    client = _build_client()

    # Convert history to Gemini Content objects
    gemini_history: list[genai_types.Content] = []
    for turn in history:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        gemini_role = "model" if role == "assistant" else "user"
        gemini_history.append(
            genai_types.Content(
                role=gemini_role,
                parts=[genai_types.Part.from_text(text=content)],
            )
        )

    chat = client.aio.chats.create(
        model=model_name,
        config=genai_types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=get_tool_declarations(),
            temperature=0.3,
        ),
        history=gemini_history,
    )

    response = await chat.send_message(message)

    # Agentic loop — resolve tool calls (max 3 rounds)
    max_iterations = 3

    for _ in range(max_iterations):
        # Collect function calls from all parts
        tool_calls = [
            part.function_call
            for part in (response.candidates[0].content.parts or [])
            if part.function_call is not None
        ]

        if not tool_calls:
            break  # No more tool calls — final answer ready

        # Execute each tool and build function response parts
        response_parts: list[genai_types.Part] = []
        for fc in tool_calls:
            tool_name = fc.name
            tool_args = dict(fc.args) if fc.args else {}
            logger.info("Tool call: %s | args=%s", tool_name, tool_args)

            result_text = _handle_tool_call(tool_name, tool_args)
            response_parts.append(
                genai_types.Part.from_function_response(
                    name=tool_name,
                    response={"result": result_text},
                )
            )

        response = await chat.send_message(response_parts)

    # Extract final text
    try:
        reply = response.text
    except Exception:
        parts = response.candidates[0].content.parts or []
        reply = " ".join(
            p.text for p in parts if hasattr(p, "text") and p.text
        )

    if not reply:
        logger.warning("Empty reply from Gemini for user=%s", user)
        reply = _FALLBACK_REPLY

    return reply
