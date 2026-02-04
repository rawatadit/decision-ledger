# Decision Ledger - Architecture Plan

## Overview

A knowledge base for capturing project decisions from various communication channels (Slack, Email), processing them with LLM to extract structured information, and making them queryable by AI agents.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      INGESTION LAYER                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Slack Bot     │   Email (Future)│   API / Web Form (Future)   │
│ @DecisionLedger │ decisions@...   │                             │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         └─────────────────┼───────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING SERVICE                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Claude API:                                                │ │
│  │  - Extract decision summary                                │ │
│  │  - Identify participants                                   │ │
│  │  - Auto-suggest project (from context + channel hints)     │ │
│  │  - Extract tags/topics                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                              │
│                     PostgreSQL (RDS)                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│  │   Projects   │ │  Decisions   │ │  Participants / Tags     │ │
│  └──────────────┘ └──────────────┘ └──────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL API                              │
│           REST API with OpenAPI spec (agent-friendly)           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Endpoints (designed as LLM tools):                         │ │
│  │  - GET /projects                                           │ │
│  │  - GET /projects/{id}/decisions                            │ │
│  │  - GET /decisions?project=&author=&date_from=&date_to=     │ │
│  │  - GET /decisions/{id}                                     │ │
│  │  - GET /decisions/search?q=                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI AGENT CONSUMERS                           │
│  Amazon Bedrock Agents │ Amazon Q │ Custom Agents │ MCP Server  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    slack_channels TEXT[],  -- hint: messages from these channels suggest this project
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Decisions Table
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),

    -- Extracted content
    summary TEXT NOT NULL,           -- LLM-extracted decision summary
    context TEXT,                    -- surrounding context/rationale
    raw_content TEXT NOT NULL,       -- original message/email

    -- Source info
    source_type VARCHAR(50) NOT NULL, -- 'slack', 'email', 'api'
    source_channel VARCHAR(255),      -- slack channel or email thread
    source_url TEXT,                  -- link back to original message
    source_timestamp TIMESTAMP,       -- when decision was made

    -- Metadata
    author VARCHAR(255),              -- who logged the decision
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Participants Table
```sql
CREATE TABLE decision_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES decisions(id) ON DELETE CASCADE,
    participant_name VARCHAR(255) NOT NULL,
    participant_role VARCHAR(100)  -- 'decider', 'approver', 'contributor'
);
```

### Tags Table
```sql
CREATE TABLE decision_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id UUID REFERENCES decisions(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL
);
CREATE INDEX idx_decision_tags_tag ON decision_tags(tag);
```

### Project Members Table
```sql
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,  -- AWS IAM user/role ARN or Slack user ID
    role VARCHAR(50) DEFAULT 'member',  -- 'admin', 'member', 'viewer'
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_project_members ON project_members(project_id, user_id);
```

---

## Component Breakdown

### 1. Slack Bot Service
**Purpose**: Listen for @DecisionLedger mentions, capture context, initiate processing

**Tech**: Python (slack-bolt library)

**Flow**:
1. User tags @DecisionLedger in a message or thread
2. Bot receives event via Slack Events API
3. Bot fetches thread context (if in thread) or surrounding messages
4. Bot sends to Processing Service
5. Processing Service returns extracted data + suggested project
6. Bot replies with confirmation

**Slack App Scopes Needed**:
- `app_mentions:read` - detect @mentions
- `channels:history` - read channel messages for context
- `chat:write` - send confirmation messages
- `reactions:write` - add ✓ reaction to logged messages

### 2. Processing Service
**Purpose**: Extract structured decision data from raw content using Claude

**Tech**: Python with Anthropic SDK

### 3. Core API Service
**Purpose**: CRUD operations + query endpoints for agents

**Tech**: Python (FastAPI)

**Key Endpoints**:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects` | GET | List all projects |
| `/projects` | POST | Create new project |
| `/projects/{id}` | GET | Get project details |
| `/projects/{id}/decisions` | GET | List decisions for a project |
| `/decisions` | GET | Query decisions (filters: project, author, date_from, date_to, tags) |
| `/decisions` | POST | Create new decision (used by ingestion services) |
| `/decisions/{id}` | GET | Get full decision details |
| `/decisions/search` | GET | Full-text search across summaries/context |

---

## Infrastructure (AWS)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Account                             │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   Lambda    │     │    ECS      │     │    RDS      │       │
│  │ Slack Bot   │────▶│  API Service│────▶│  PostgreSQL │       │
│  │ (or Fargate)│     │  (Fargate)  │     │             │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│         │                   │                                   │
│         │                   │                                   │
│         ▼                   ▼                                   │
│  ┌─────────────┐     ┌─────────────┐                           │
│  │ API Gateway │     │  Bedrock    │                           │
│  │ (Slack URL) │     │   Agent     │                           │
│  └─────────────┘     └─────────────┘                           │
│                                                                 │
│  ┌─────────────┐                                               │
│  │  Secrets    │  (Slack tokens, Claude API key)               │
│  │  Manager    │                                               │
│  └─────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack Summary

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| API Framework | FastAPI |
| Database | PostgreSQL (AWS RDS) |
| LLM | Claude API (Anthropic) |
| Slack | slack-bolt (Python) |
| Deployment | AWS ECS Fargate |
| IaC | CDK or Terraform (optional) |
| Agent | AWS Bedrock Agent |
