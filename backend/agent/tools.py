"""Tool declarations and hardcoded tool handlers for the SupportIQ agent."""

from google.genai import types as genai_types

# ---------------------------------------------------------------------------
# Hardcoded response constants
# ---------------------------------------------------------------------------

PRICING_RESPONSE = """
**SupportIQ Pricing Plans**

- **Starter** — $399/month
  Up to 20 NDIS participants | Full platform included

- **Growth** — $799/month
  Up to 40 NDIS participants | Full platform included

- **Enterprise** — Custom pricing
  Unlimited participants | White-label options | Dedicated support

All plans include: NDIS billing automation, SCHADS payroll engine, DEX reporting, smart rostering, caregiver mobile app, and CEO analytics dashboard.

📅 Book a free 20-minute demo: https://calendly.com/matthew-support-iq/30min
💬 WhatsApp Matthew: +61 424 046 730
📧 Email: matthew@support-iq.com.au
"""

DEMO_RESPONSE = """
**Book a Free SupportIQ Demo**

Matthew will walk you through the platform using your specific use case — NDIS billing, SCHADS payroll, DEX reporting, or the full platform.

📅 Book here (takes 30 seconds): https://calendly.com/matthew-support-iq/30min
💬 WhatsApp: +61 424 046 730
📧 Email: matthew@support-iq.com.au

Demos are free, 20 minutes, and tailored to your organisation's needs.
"""

DOMAIN_MAP: dict[str, str] = {
    "ndis": "ndis",
    "product": "product",
    "all": "all",
}


# ---------------------------------------------------------------------------
# Gemini FunctionDeclaration helpers
# ---------------------------------------------------------------------------


def get_tool_declarations() -> list[genai_types.Tool]:
    """Return the list of Gemini Tool objects used by the orchestrator."""

    search_ndis = genai_types.FunctionDeclaration(
        name="search_ndis_knowledge",
        description=(
            "Search the NDIS billing rules, price guide, and PRODA claims knowledge base."
        ),
        parameters=genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                "query": genai_types.Schema(
                    type=genai_types.Type.STRING,
                    description="The NDIS-related question or keyword to search for.",
                )
            },
            required=["query"],
        ),
    )

    search_product = genai_types.FunctionDeclaration(
        name="search_product_knowledge",
        description=(
            "Search SupportIQ platform features, modules, integrations, and FAQ."
        ),
        parameters=genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                "query": genai_types.Schema(
                    type=genai_types.Type.STRING,
                    description="The SupportIQ product question or keyword to search for.",
                )
            },
            required=["query"],
        ),
    )

    get_demo_or_pricing = genai_types.FunctionDeclaration(
        name="get_demo_or_pricing",
        description=(
            "Get SupportIQ pricing plans or demo booking information. "
            "Use this for ANY question about price, cost, plans, or booking a demo."
        ),
        parameters=genai_types.Schema(
            type=genai_types.Type.OBJECT,
            properties={
                "intent": genai_types.Schema(
                    type=genai_types.Type.STRING,
                    description=(
                        "Either 'pricing' to get plan costs or 'demo' to get "
                        "demo booking details."
                    ),
                )
            },
            required=["intent"],
        ),
    )

    return [
        genai_types.Tool(
            function_declarations=[
                search_ndis,
                search_product,
                get_demo_or_pricing,
            ]
        )
    ]
