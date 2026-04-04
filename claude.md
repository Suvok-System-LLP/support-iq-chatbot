# CLAUDE.md — SupportIQ Chatbot Project

> This file is the single source of truth for Claude Code working on this project.
> Read this entire file before writing any code.

---

## WHAT THIS PROJECT IS

A standalone AI-powered chatbot for **SupportIQ** — an Australian NDIS compliance SaaS platform built by RM Consultancy. The chatbot lives at `https://support-iq.com.au/chatbot.html` and is the primary lead generation and education tool for NDIS service providers across Australia.

The chatbot answers questions about:

- SCHADS Award pay rates, penalty rates, overtime, allowances
- NDIS billing rules, price guide, PRODA claim submission
- DEX / DSS reporting requirements and SCORE metrics
- SupportIQ platform features, pricing, and demo booking

This is NOT the main SupportIQ platform (that is a separate monorepo at `github.com/suvoksystem/supportiq-platform`). This is only the public-facing marketing chatbot with an agentic RAG backend.

---

## TECH STACK

| Layer         | Technology                                           |
| ------------- | ---------------------------------------------------- |
| Frontend      | HTML/CSS/JS — already deployed on Netlify            |
| Backend API   | Python 3.12 + FastAPI                                |
| LLM           | Gemini 1.5 Flash via `google-generativeai`           |
| Embeddings    | `text-embedding-004` via Vertex AI                   |
| Vector Store  | Vertex AI Vector Search                              |
| RAG Framework | LangChain                                            |
| Deployment    | Cloud Run (backend) + Netlify (frontend)             |
| Region        | `australia-southeast1` — mandatory, data sovereignty |

---

## REPO STRUCTURE

```
supportiq-chatbot/
├── CLAUDE.md                   ← you are here
├── README.md
├── frontend/
│   ├── index.html              ← SupportIQ marketing landing page (do not modify design)
│   ├── chatbot.html            ← Standalone chatbot UI (only change: CHATBOT_ENDPOINT URL)
│   └── netlify.toml            ← Netlify routing config
├── backend/
│   ├── main.py                 ← FastAPI app, POST /chat entry point
│   ├── agent/
│   │   ├── orchestrator.py     ← Gemini agentic router with function calling
│   │   └── tools.py            ← Tool declarations + hardcoded tool handlers
│   ├── rag/
│   │   ├── retriever.py        ← Vertex AI Vector Search retrieval
│   │   ├── embedder.py         ← text-embedding-004 wrapper
│   │   └── chunker.py          ← Markdown doc chunking with tiktoken
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── knowledge/                  ← RAG corpus — all markdown files ingested into vector store
│   ├── schads/
│   │   ├── overview.md
│   │   ├── pay_rates.md
│   │   ├── penalty_rates.md
│   │   └── allowances.md
│   ├── ndis/
│   │   ├── billing_rules.md
│   │   ├── price_guide.md
│   │   └── proda_claims.md
│   ├── dex/
│   │   ├── reporting_guide.md
│   │   └── score_requirements.md
│   └── product/
│       ├── features.md
│       ├── pricing.md
│       └── faq.md
└── scripts/
    ├── ingest_docs.py          ← Run once to build Vertex AI index
    └── test_agent.py           ← Interactive CLI test loop
```

---

## DOMAIN KNOWLEDGE — READ THIS CAREFULLY

### About SCHADS Award

The Social, Community, Home Care and Disability Services (SCHADS) Industry Award 2010 governs pay for all support workers in Australia.

Key rules the chatbot must know:

- Classifications: Level 1–8 across Social and Community Services, Home Care, and Crisis Accommodation streams
- Casual loading: 25% on top of base rate
- Penalty rates: Saturday 150%, Sunday 200%, Public Holiday 250%
- Overtime: after 38 hours/week or agreed ordinary hours
- Minimum engagement: 2 hours per shift for casual and part-time workers
- Allowances: travel, broken shift, on-call, overnight, protective clothing
- Span of ordinary hours: Monday–Saturday 6am–10pm, Sunday 8am–10pm
- Broken shift allowance applies when there is an unpaid break of 2+ hours

### About NDIS

The National Disability Insurance Scheme funds supports for Australians with permanent and significant disability.

Key rules the chatbot must know:

- Three funding categories: Core Supports, Capacity Building, Capital Supports
- NDIS Price Guide sets maximum hourly rates per support item
- PRODA is the government portal for submitting payment claims
- Payment requests must match: participant NDIS number, support item code, date of service, registered provider number
- Common rejection reasons: expired plan, wrong support category, rate above price guide, unregistered provider
- Plans are reviewed annually — claims must fall within plan dates

### About DEX Reporting

Data Exchange (DEX) is the DSS (Department of Social Services) reporting framework.

Key rules the chatbot must know:

- Providers receiving DSS funding must submit DEX reports
- SCORE metrics: 3 measures captured per session — Circumstances (living situation), Goals progress, Satisfaction with service (each rated 1–5)
- SLK (Statistical Linkage Key): a de-identified key derived from client name + DOB + gender, used instead of real names in DEX
- Reporting periods: typically 6-monthly (Jan–Jun and Jul–Dec)
- Minimum SCORE completeness: 95% of sessions must have SCORE data captured
- XML format submission to DSS portal

### About SupportIQ Platform

**What it does:**
SupportIQ is a purpose-built agentic AI platform that automates NDIS compliance for Australian service providers. It replaces legacy tools like CareMaster.

**Core modules:**

- NDIS Billing Automation — AI validates claims against price guide, submits to PRODA
- SCHADS Payroll Engine — automatic classification, penalty rates, payslips
- DEX Compliance — auto-collects SCORE data from shifts, generates and submits DSS XML
- Smart Rostering — auto-fills rosters respecting SCHADS shift rules
- Caregiver Mobile App — GPS clock-in, guided SCORE capture, incident reporting
- CEO Dashboard — revenue, plan utilisation, compliance status in real time
- Audit Readiness — always-on compliance vault

**Pricing (do not deviate from these):**

- Starter: $399/month — up to 20 NDIS participants, full platform
- Growth: $799/month — up to 40 NDIS participants, full platform
- Enterprise: Custom pricing — unlimited participants, white-label, dedicated support

**Who it's for:**
NDIS registered service providers in Australia — particularly those currently using CareMaster or similar legacy software and struggling with manual compliance work.

**Contact:**

- Demo booking: https://calendly.com/matthew-support-iq/30min
- Email: matthew@support-iq.com.au
- WhatsApp: +61 424 046 730
- Website: https://support-iq.com.au

---

## CHATBOT AGENT BEHAVIOUR RULES

These rules govern how the chatbot agent must behave. Enforce these in the system prompt and orchestrator logic.

1. **Always retrieve before answering** — for any SCHADS, NDIS, or DEX question, always call the RAG retriever first. Never answer compliance questions from memory alone.

2. **Pricing is hardcoded** — never use RAG for pricing. Always use the `get_demo_or_pricing` tool which returns the exact pricing constants. Do not invent or approximate prices.

3. **Always end product answers with a CTA** — when answering a question about SupportIQ features, end with a soft call-to-action: "Want to see this in action? Book a free 20-minute demo with Matthew: https://calendly.com/matthew-support-iq/30min"

4. **Warm, professional tone** — not robotic. Write like a knowledgeable NDIS compliance expert who genuinely wants to help. Short paragraphs, plain English, no jargon dumps.

5. **Never make up specific numbers** — if the RAG retrieval doesn't return a specific rate, say "I'd recommend checking the current NDIS Price Guide or SCHADS Award for the exact figure, as rates are updated regularly."

6. **Never promise features not in the platform** — if asked about a feature SupportIQ doesn't have, say it's not available yet and offer to pass the feedback to the team via the demo booking.

7. **Lead capture is done** — the lead gate in the frontend already captures name + email before the chat starts. Don't ask for personal details in the chat.

8. **Escalation path** — for complex or custom questions, always direct to: "Book a call with Matthew — https://calendly.com/matthew-support-iq/30min"

---

## ENVIRONMENT VARIABLES

All secrets and config live in `.env` (local) or GCP Secret Manager (production). Never hardcode.

```
GOOGLE_CLOUD_PROJECT        GCP project ID
GOOGLE_CLOUD_REGION         australia-southeast1
VERTEX_INDEX_ENDPOINT_ID    Vertex AI Vector Search endpoint ID
VERTEX_DEPLOYED_INDEX_ID    Deployed index ID within the endpoint
GEMINI_MODEL                gemini-1.5-flash
EMBEDDING_MODEL             text-embedding-004
ALLOWED_ORIGINS             https://support-iq.com.au,https://supportiq.com.au
PORT                        8080
```

---

## DEVELOPMENT COMMANDS

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run locally
cd backend && uvicorn main:app --reload --port 8080

# Test the agent interactively
python scripts/test_agent.py

# Ingest knowledge base into Vertex AI (run once, re-run when docs change)
python scripts/ingest_docs.py

# Re-ingest a single domain only
python scripts/ingest_docs.py --domain schads

# Dry run (no upload, just print chunks)
python scripts/ingest_docs.py --dry-run

# Build Docker image
cd backend && docker build -t supportiq-chatbot .

# Deploy to Cloud Run
gcloud run deploy supportiq-chatbot \
  --source ./backend \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

---

## API CONTRACT

### POST /chat

Request:

```json
{
  "message": "What are the SCHADS penalty rates for Sunday?",
  "history": [
    { "role": "user", "content": "previous message" },
    { "role": "assistant", "content": "previous reply" }
  ],
  "user": "Sarah"
}
```

Response:

```json
{
  "reply": "Sunday shifts under the SCHADS Award attract a 200% penalty rate..."
}
```

### GET /health

Response:

```json
{ "status": "ok" }
```

---

## FRONTEND INTEGRATION

The only change needed in `frontend/chatbot.html` is this one line:

```javascript
// Change this:
const CHATBOT_ENDPOINT = "https://api.support-iq.com.au/chat";

// To your Cloud Run URL during development:
const CHATBOT_ENDPOINT = "https://YOUR-CLOUD-RUN-URL/chat";

// Then back to production URL before final deploy:
const CHATBOT_ENDPOINT = "https://api.support-iq.com.au/chat";
```

Do NOT modify anything else in the HTML files. The frontend design is final.

---

## CODE STANDARDS

- Python 3.12+ with full type hints on every function
- Docstrings on every public function
- `python-dotenv` for all env vars — no os.environ.get without a default
- Structured logging with timestamps — no bare `print()` in production code
- Error handling on every external call (Vertex AI, Gemini) — always return a graceful fallback reply, never crash the endpoint
- No real participant data ever — this is a marketing chatbot, zero PII
