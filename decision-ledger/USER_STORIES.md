# Decision Ledger - User Stories & Product Requirements

> **Status:** Approved
> **Last Updated:** 2024-02-03
> **Owner:** Aditya

---

## Table of Contents

1. [Overview](#overview)
2. [User Personas](#user-personas)
3. [User Stories](#user-stories)
   - [Decision Capture](#decision-capture)
   - [Decision Retrieval](#decision-retrieval)
   - [Project Management](#project-management)
   - [Agent Integration](#agent-integration)
4. [Product Decisions](#product-decisions)
5. [Acceptance Criteria](#acceptance-criteria)
6. [Open Questions](#open-questions)
7. [Out of Scope (v1)](#out-of-scope-v1)

---

## Overview

Decision Ledger aggregates project decisions from multiple sources (Slack, meeting summaries, direct API) into a unified, queryable knowledge base. This document captures the product requirements as user stories.

### Core Jobs to Be Done

| Job | Current Solution | Decision Ledger Solution |
|-----|------------------|-------------------------|
| Capture a decision when it's made | Manual documentation (rarely done) | Tag @DecisionLedger or auto-ingest from meetings |
| Find what was decided about X | Search Slack history, ask teammates | Query unified API or ask AI agent |
| Understand decision context | Re-read old threads, rely on memory | Stored context, participants, and rationale |
| Give AI agents access to decisions | Not possible | Agent-friendly REST API |

---

## User Personas

### 1. Team Member
> Someone who participates in decisions and needs to find past decisions.

**Goals:**
- Easily capture decisions without disrupting workflow
- Find past decisions quickly
- Understand context and rationale behind decisions

**Frustrations:**
- Decisions get lost in Slack threads
- Can't remember what was decided or why
- Has to ask teammates repeatedly

---

### 2. Project Admin
> Someone who manages a project and its team membership.

**Goals:**
- Organize decisions by project
- Control who can see project decisions
- Ensure important decisions are captured

**Frustrations:**
- No central place for project decisions
- Team members leave and knowledge is lost

---

### 3. AI Agent
> An automated system (Bedrock Agent, MCP client, etc.) that answers questions about decisions.

**Goals:**
- Query decisions programmatically
- Filter by project, date, author, tags
- Get structured, reliable responses

**Frustrations:**
- No API access to decision history
- Data scattered across tools

---

## User Stories

### Decision Capture

#### DC-1: Capture decision from Slack message
> **As a** team member
> **I want to** tag @DecisionLedger in a Slack message
> **So that** the decision is captured without leaving Slack

**Details:**
- Bot shows preview with extracted summary (pending state)
- User must confirm before decision is saved
- Original message gets ✓ reaction after confirmation

**Example:**
```
User: "We're going with PostgreSQL for the new service @DecisionLedger"

Bot: 📝 Preview - not yet saved
     Project: Backend Rewrite
     Summary: Use PostgreSQL for the new service

     [Save as Final] [Save as Open] [Change Project] [Cancel]

User: clicks "Save as Final"

Bot: ✓ Decision saved to Backend Rewrite
```

**Note:** No inline editing. If summary is wrong, user cancels and re-tags with clearer message.

---

#### DC-2: Capture decision with thread context
> **As a** team member
> **I want to** tag @DecisionLedger in a thread
> **So that** the full discussion context is captured with the decision

**Details:**
- Bot fetches entire thread for context
- Claude extracts decision from thread, not just the tagged message
- Participants from thread are captured

---

#### DC-3: Auto-ingest meeting decisions
> **As a** team member
> **I want** meeting decisions to be automatically captured from meeting bot summaries
> **So that** I don't have to manually log them

**Details:**
- Meeting bot sends email to dedicated address (e.g., decisions@domain.com)
- System parses "Decisions" section from structured email
- Each bullet becomes a separate decision
- Status (pending vs confirmed) configurable per project

**Email Format:**
```
Meeting summary
[paragraph summary]

Decisions
* Decision 1
* Decision 2

Next steps
* Action item 1
```

**Configuration:**
- `MEETING_BOT_SENDER` - email address of meeting bot
- `MEETING_EMAIL_SUBJECT_PATTERN` - subject line pattern to match
- Project setting: `auto_confirm_meeting_decisions` (boolean)

---

#### DC-4: Preview and confirm before saving
> **As a** team member
> **I want to** see the extracted summary before saving
> **So that** I can verify accuracy

**Details:**
- Bot shows preview with: project, summary, status options
- User can change project in preview phase
- No inline summary editing - if wrong, cancel and re-tag with clearer message
- Once confirmed, decision is immutable
- Unconfirmed decisions stay in `pending` state indefinitely

---

#### DC-5: Choose decision status when saving
> **As a** team member
> **I want to** mark a decision as "open" (still discussing) or "final"
> **So that** the team knows which decisions are settled

**Statuses:**
| Status | Meaning |
|--------|---------|
| `pending` | Awaiting user confirmation (preview state) |
| `open` | Logged but decision not finalized yet |
| `confirmed` | Final decision |
| `superseded` | Replaced by a newer decision |

---

#### DC-6: Auto-suggest project for decision
> **As a** team member
> **I want** the system to suggest the right project based on channel and content
> **So that** I don't have to manually categorize every decision

**Details:**
- System uses channel-to-project mapping
- Claude suggests project based on content
- User can override if suggestion is wrong

---

#### DC-7: Create project when no match
> **As a** team member
> **I want to** create a new project if none of the existing ones match
> **So that** my decision is properly categorized

**Flow (Slack):**
```
Bot: I couldn't match this to an existing project.

     [Create New Project] [Select Existing ▾]

User: clicks "Create New Project"

Bot: What should the project be called?

User: "Infrastructure Migration"

Bot: ✓ Created project "Infrastructure Migration"
     ✓ Decision logged
```

---

#### DC-8: Update a decision by superseding
> **As a** team member
> **I want to** update a previous decision by logging a new one that references it
> **So that** we have an audit trail of how decisions evolved

**Details:**
- Decisions are immutable after confirmation
- To "update", create new decision with `supersedes_id` pointing to original
- Original decision no longer appears in default queries
- History endpoint shows full evolution

**Example:**
```
Original:  "Launch date is March 15th" (id: abc)
    ↓
Update:    "Launch date moved to April 1st" (supersedes_id: abc)
```

---

#### DC-9: Resolve an open decision
> **As a** team member
> **I want to** mark an open decision as resolved with the final answer
> **So that** the team knows the discussion concluded

**Details:**
- Create new `confirmed` decision that supersedes the `open` one
- History shows: open discussion → final decision

---

#### DC-10: Create decision via direct API
> **As a** developer
> **I want to** POST decisions directly to the API
> **So that** I can integrate other tools with Decision Ledger

**Details:**
- Accepts structured or raw content
- If raw, Claude extracts structure
- Returns decision ID

---

### Decision Retrieval

#### DR-1: Search decisions by keyword
> **As a** team member
> **I want to** search decisions by keyword
> **So that** I can find what we decided about a topic

**Details:**
- Full-text search across summary and context
- Results ranked by relevance
- **Only returns latest in supersede chain** (not superseded decisions)
- Shows project, date, and summary in results

---

#### DR-2: Filter decisions by project
> **As a** team member
> **I want to** see all decisions for a specific project
> **So that** I can review project history

**Details:**
- Filter by single project
- Sorted by date (newest first)
- Excludes superseded decisions by default

---

#### DR-3: Filter decisions by date range
> **As a** team member
> **I want to** filter decisions by date range
> **So that** I can see what was decided during a period

---

#### DR-4: Filter decisions by author
> **As a** team member
> **I want to** see decisions logged by a specific person
> **So that** I can review their decisions

---

#### DR-5: Filter decisions by tags
> **As a** team member
> **I want to** filter decisions by tags
> **So that** I can find decisions on specific topics

---

#### DR-6: Filter decisions by status
> **As a** team member
> **I want to** filter decisions by status (open vs confirmed)
> **So that** I can see what's still being discussed

---

#### DR-7: View decision details
> **As a** team member
> **I want to** see full details of a decision
> **So that** I understand the context and participants

**Details:**
- Shows: summary, context, participants, tags, source link, status
- Indicates if decision was superseded (with link to newer version)

---

#### DR-8: View decision history
> **As a** team member
> **I want to** see how a decision evolved over time
> **So that** I understand the context of changes

**Endpoint:** `GET /decisions/{id}/history`

**Returns:**
```json
{
  "chain": [
    {"id": "abc", "summary": "Launch March 15", "status": "superseded", "created_at": "..."},
    {"id": "def", "summary": "Launch April 1", "status": "confirmed", "created_at": "..."}
  ],
  "current": "def"
}
```

---

#### DR-9: Include superseded decisions
> **As a** team member
> **I want to** optionally include superseded decisions in search
> **So that** I can see the full history

**Parameter:** `?include_superseded=true`

---

#### DR-10: Access decision source
> **As a** team member
> **I want to** click through to the original Slack message or email
> **So that** I can see the full original discussion

---

### Project Management

#### PM-1: Create a project
> **As a** project admin
> **I want to** create a project
> **So that** decisions can be organized under it

**Fields:**
- `name` - unique project name
- `description` - project description
- `slack_channels[]` - channels that map to this project
- `auto_confirm_meeting_decisions` - boolean (default: false)
- `notification_channel` - optional, for future notifications

---

#### PM-2: Add members to project
> **As a** project admin
> **I want to** add team members to a project
> **So that** they can see project decisions

**Roles:** admin, member, viewer

---

#### PM-3: Remove members from project
> **As a** project admin
> **I want to** remove members from a project
> **So that** access is controlled when people leave

---

#### PM-4: Only see my projects' decisions
> **As a** team member
> **I want to** only see decisions for projects I'm a member of
> **So that** access is properly scoped

---

#### PM-5: Map Slack channels to projects
> **As a** project admin
> **I want to** associate Slack channels with a project
> **So that** decisions from those channels auto-categorize

---

### Agent Integration

#### AI-1: Agent lists user's projects
> **As an** AI agent
> **I want to** list projects the user has access to
> **So that** I can help them navigate their decisions

---

#### AI-2: Agent searches decisions
> **As an** AI agent
> **I want to** search decisions by query
> **So that** I can answer "what did we decide about X?"

---

#### AI-3: Agent gets decision details
> **As an** AI agent
> **I want to** get full details of a specific decision
> **So that** I can provide complete context to the user

---

#### AI-4: Agent queries by filters
> **As an** AI agent
> **I want to** query decisions with filters (project, date, author, status)
> **So that** I can answer specific questions

**Example queries:**
- "What decisions did we make last week?"
- "What open discussions do we have?"
- "Show me all database-related decisions"

---

## Product Decisions

> Key decisions made during requirements gathering.

| # | Topic | Decision | Rationale |
|---|-------|----------|-----------|
| PD-1 | Editing | Decisions are immutable after confirmation | Simplicity, audit trail |
| PD-2 | Updating | Create superseding decision with reference | Maintains history |
| PD-3 | Statuses | pending, open, confirmed, superseded | Captures full lifecycle |
| PD-4 | Preview | Show preview before saving, no inline editing | Simplicity; cancel and re-tag if wrong |
| PD-5 | Pending timeout | Stay pending indefinitely | Don't auto-confirm potentially wrong data |
| PD-6 | Query default | Only show latest (non-superseded) decisions | Cleaner results |
| PD-7 | History | Available via dedicated endpoint | Audit trail accessible |
| PD-8 | Email auto-confirm | Configurable per project | Flexibility |
| PD-9 | Slash command | Designed for, not P0 | Future flexibility |
| PD-10 | Notifications | Designed for, not P0 | Future flexibility |

---

## Acceptance Criteria

### Decision Capture

| ID | Criterion |
|----|-----------|
| AC-DC-1 | @mention shows preview within 5 seconds |
| AC-DC-2 | Preview includes summary, project, status options |
| AC-DC-3 | User can change project before confirming |
| AC-DC-4 | User can cancel and re-tag if summary is wrong |
| AC-DC-5 | Confirmed decisions are immutable |
| AC-DC-6 | ✓ reaction added after confirmation |
| AC-DC-7 | Meeting email parsed within 1 minute of receipt |
| AC-DC-8 | Each bullet in "Decisions" section becomes separate decision |

### Decision Retrieval

| ID | Criterion |
|----|-----------|
| AC-DR-1 | Search excludes superseded decisions by default |
| AC-DR-2 | `?include_superseded=true` includes full history |
| AC-DR-3 | History endpoint returns full chain |
| AC-DR-4 | Users only see decisions from their projects |
| AC-DR-5 | Filter by status works (open, confirmed) |

### Superseding

| ID | Criterion |
|----|-----------|
| AC-SS-1 | New decision can reference `supersedes_id` |
| AC-SS-2 | Superseded decision hidden from default queries |
| AC-SS-3 | History shows evolution from open → confirmed |

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | How should project creation work in read-only interfaces (non-agentic)? | **TBD** |
| Q2 | Should there be a web UI for browsing/confirming decisions? | **Phase 2** |

---

## Out of Scope (v1)

| Feature | Reason | Future Phase |
|---------|--------|--------------|
| Web UI | Focus on API-first | Phase 2 |
| `/decision` slash command | Not P0 | Phase 2 |
| Channel notifications | Not P0 | Phase 2 |
| Decision attachments | Complexity | Phase 2 |
| Decision comments | Keep simple | Phase 2 |
| Pending decision reminders | Not P0 | Phase 2 |
| Multiple Slack workspaces | Single workspace first | Phase 3 |

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-02-03 | Aditya | Initial draft |
| 2024-02-03 | Aditya | Added product decisions from Q&A session |
