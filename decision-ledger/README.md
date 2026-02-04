# Decision Ledger

A knowledge base for capturing project decisions from Slack, processing them with Claude to extract structured information, and making them queryable by AI agents.

## Features

- **Slack Integration**: Tag `@DecisionLedger` in any message or thread to capture a decision
- **AI-Powered Extraction**: Claude extracts decision summaries, participants, and tags
- **Project Organization**: Decisions are automatically associated with projects
- **Agent-Friendly API**: REST API designed for consumption by AI agents (Bedrock, MCP, etc.)

## Architecture

See [DESIGN.md](./DESIGN.md) for detailed architecture documentation.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Slack workspace with admin access (for bot setup)
- Anthropic API key

### Local Development

1. **Clone and setup environment**:
   ```bash
   cd decision-ledger
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Start the database**:
   ```bash
   docker-compose up -d postgres
   ```

3. **Run database migrations**:
   ```bash
   docker-compose exec postgres psql -U postgres -d decision_ledger -f /docker-entrypoint-initdb.d/001_initial_schema.sql
   ```

4. **Start the API service**:
   ```bash
   cd services/api
   pip install -r requirements.txt
   uvicorn src.main:app --reload --port 8000
   ```

5. **Start the Slack bot** (requires ngrok for local development):
   ```bash
   cd services/slack-bot
   pip install -r requirements.txt
   python src/app.py
   ```

### Slack App Setup

1. Create a new Slack App at https://api.slack.com/apps
2. Add the following OAuth scopes:
   - `app_mentions:read`
   - `channels:history`
   - `chat:write`
   - `reactions:write`
3. Enable Event Subscriptions and subscribe to `app_mention` events
4. Install the app to your workspace
5. Copy the Bot Token and Signing Secret to your `.env` file

## Project Structure

```
decision-ledger/
├── DESIGN.md                    # Architecture documentation
├── README.md                    # This file
├── docker-compose.yml           # Local development environment
├── .env.example                 # Environment variables template
├── .gitignore
│
├── database/
│   └── migrations/
│       └── 001_initial_schema.sql
│
├── services/
│   ├── api/                     # Core API service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── main.py
│   │       ├── models/
│   │       ├── routes/
│   │       └── db/
│   │
│   ├── processor/               # Claude extraction service
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── extractor.py
│   │       └── prompts.py
│   │
│   └── slack-bot/               # Slack integration
│       ├── requirements.txt
│       └── src/
│           ├── app.py
│           └── handlers/
│
└── infrastructure/              # AWS CDK or Terraform (Phase 6)
    └── ...
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/projects` | GET | List all projects |
| `/projects` | POST | Create new project |
| `/projects/{id}` | GET | Get project details |
| `/projects/{id}/decisions` | GET | List decisions for a project |
| `/projects/{id}/members` | GET/POST | Manage project members |
| `/decisions` | GET | Query decisions with filters |
| `/decisions` | POST | Create new decision |
| `/decisions/{id}` | GET | Get decision details |
| `/decisions/search` | GET | Full-text search |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `ANTHROPIC_API_KEY` | Claude API key |
| `SLACK_BOT_TOKEN` | Slack Bot OAuth token |
| `SLACK_SIGNING_SECRET` | Slack app signing secret |
| `API_BASE_URL` | Base URL for the API service |

## License

MIT
