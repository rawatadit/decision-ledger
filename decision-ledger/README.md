# Decision Ledger

> A unified knowledge base that aggregates project decisions from multiple sources and makes them queryable by AI agents.

---

## The Problem

Decisions are made everywhere—Slack threads, meetings, emails—but queryable nowhere. When someone asks "what did we decide about X?", the answer is buried across multiple tools.

## The Solution

Decision Ledger aggregates decisions from all sources into a single, searchable knowledge base with an AI-agent-friendly API.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Slack Bot      │     │  Meeting Bot    │     │  Direct API     │
│  @DecisionLedger│     │  Email Summary  │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌────────────────────────┐
                    │    Decision Ledger     │
                    │  ┌──────────────────┐  │
                    │  │ Claude Extraction│  │
                    │  └──────────────────┘  │
                    │  ┌──────────────────┐  │
                    │  │ PostgreSQL Store │  │
                    │  └──────────────────┘  │
                    │  ┌──────────────────┐  │
                    │  │   REST API       │  │
                    │  └──────────────────┘  │
                    └───────────┬────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
        ┌───────────┐    ┌───────────┐    ┌───────────┐
        │  Bedrock  │    │    MCP    │    │  Web UI   │
        │  Agents   │    │  Clients  │    │ (Future)  │
        └───────────┘    └───────────┘    └───────────┘
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [DESIGN.md](./DESIGN.md) | Technical architecture and design decisions |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Phased implementation plan with tasks |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Slack workspace with admin access
- Anthropic API key

### 1. Clone and Configure

```bash
cd decision-ledger
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start Database

```bash
docker-compose up -d postgres
```

### 3. Run API

```bash
cd services/api
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 4. Run Slack Bot (requires ngrok)

```bash
cd services/slack-bot
pip install -r requirements.txt
python src/app.py
```

---

## Project Structure

```
decision-ledger/
├── DESIGN.md                 # Architecture documentation
├── IMPLEMENTATION_PLAN.md    # Detailed implementation plan
├── README.md                 # This file
├── docker-compose.yml        # Local development setup
├── .env.example              # Environment template
│
├── database/
│   └── migrations/           # SQL schema files
│
└── services/
    ├── api/                  # REST API (FastAPI)
    ├── processor/            # Claude extraction service
    └── slack-bot/            # Slack integration
```

---

## How It Works

### 1. Slack Capture

```
User: "Let's go with PostgreSQL for the new service @DecisionLedger"

Bot: ✓ Decision logged to **Backend Rewrite**
     Summary: Use PostgreSQL for the new service
     [View] [Edit Project]
```

### 2. Meeting Email Ingestion

Meeting bot sends summary email → Decision Ledger extracts "Key Decisions" section → Each decision stored with meeting context.

### 3. Query via Agent

```
Human: "What database decisions have we made for the backend rewrite?"

Agent: Based on the Decision Ledger, you decided on 2024-02-01 to use
       PostgreSQL for the new service. The decision was made by Alice
       with Bob's approval, citing better full-text search support.
```

---

## API Overview

| Endpoint | Description |
|----------|-------------|
| `GET /projects` | List all projects |
| `GET /projects/{id}/decisions` | Get project decisions |
| `GET /decisions` | Query with filters |
| `GET /decisions/search?q=` | Full-text search |
| `POST /decisions` | Create decision |

Full API docs available at `/docs` when running.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Claude API key |
| `SLACK_BOT_TOKEN` | Slack bot OAuth token |
| `SLACK_SIGNING_SECRET` | Slack app signing secret |

---

## License

MIT
