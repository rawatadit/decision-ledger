# Decision Ledger - User Stories & Product Requirements

> **Status:** Draft - Needs Review
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
4. [Acceptance Criteria](#acceptance-criteria)
5. [Open Questions](#open-questions)
6. [Out of Scope (v1)](#out-of-scope-v1)

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
- Bot should respond with confirmation
- Decision summary should be extracted automatically
- Original message should get a ✓ reaction

**Example:**
```
User: "We're going with PostgreSQL for the new service @DecisionLedger"

Bot: ✓ Decision logged to **Backend Rewrite**
     Summary: Use PostgreSQL for the new service
```

---

#### DC-2: Capture decision with thread context
> **As a** team member
> **I want to** tag @DecisionLedger in a thread
> **So that** the full discussion context is captured with the decision

**Details:**
- Bot should fetch entire thread for context
- Claude extracts decision from thread, not just the tagged message
- Participants from thread should be captured

---

#### DC-3: Auto-ingest meeting decisions
> **As a** team member
> **I want** meeting decisions to be automatically captured from meeting bot summaries
> **So that** I don't have to manually log them

**Details:**
- Meeting bot sends email summary to designated address
- System parses "Key Decisions" section
- Each decision stored with meeting metadata (attendees, date, project)

---

#### DC-4: Confirm and correct extracted decision
> **As a** team member
> **I want to** see the extracted summary and correct it if wrong
> **So that** the decision record is accurate

**Details:**
- Bot shows extracted summary in confirmation message
- User can click "Edit" to modify summary
- User can click "Change Project" to reassign

**Open Question:** How should editing work? Inline in Slack? Modal?

---

#### DC-5: Auto-suggest project for decision
> **As a** team member
> **I want** the system to suggest the right project based on channel and content
> **So that** I don't have to manually categorize every decision

**Details:**
- System uses channel-to-project mapping
- Claude suggests project based on content
- User can override if suggestion is wrong

---

#### DC-6: Create decision via direct API
> **As a** developer
> **I want to** POST decisions directly to the API
> **So that** I can integrate other tools with Decision Ledger

**Details:**
- Accepts structured or raw content
- If raw, Claude extracts structure
- Returns decision ID and confirmation

---

### Decision Retrieval

#### DR-1: Search decisions by keyword
> **As a** team member
> **I want to** search decisions by keyword
> **So that** I can find what we decided about a topic

**Details:**
- Full-text search across summary and context
- Results ranked by relevance
- Shows project, date, and summary in results

---

#### DR-2: Filter decisions by project
> **As a** team member
> **I want to** see all decisions for a specific project
> **So that** I can review project history

**Details:**
- Filter by single project
- Sorted by date (newest first)
- Shows summary, author, source type

---

#### DR-3: Filter decisions by date range
> **As a** team member
> **I want to** filter decisions by date range
> **So that** I can see what was decided during a period

**Details:**
- Accepts date_from and date_to parameters
- Uses source_timestamp (when decision was made)

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

**Details:**
- Tags are auto-extracted by Claude
- Filter accepts multiple tags (OR logic)

---

#### DR-6: View decision details
> **As a** team member
> **I want to** see full details of a decision
> **So that** I understand the context and participants

**Details:**
- Shows: summary, context, participants, tags, source link
- Link to original Slack message/email thread if available

---

#### DR-7: Access decision source
> **As a** team member
> **I want to** click through to the original Slack message or email
> **So that** I can see the full original discussion

**Details:**
- source_url stored for each decision
- Link works if user has access to original source

---

### Project Management

#### PM-1: Create a project
> **As a** project admin
> **I want to** create a project
> **So that** decisions can be organized under it

**Details:**
- Project has: name, description, slack_channels[]
- slack_channels used for auto-suggestion hints

---

#### PM-2: Add members to project
> **As a** project admin
> **I want to** add team members to a project
> **So that** they can see project decisions

**Details:**
- Members identified by Slack user ID or IAM ARN
- Roles: admin, member, viewer

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

**Details:**
- All API queries automatically filtered by membership
- Cannot query decisions for projects user isn't in

---

#### PM-5: Map Slack channels to projects
> **As a** project admin
> **I want to** associate Slack channels with a project
> **So that** decisions from those channels auto-categorize

**Details:**
- Project has slack_channels[] array
- Decisions from mapped channels suggest that project

---

### Agent Integration

#### AI-1: Agent lists user's projects
> **As an** AI agent
> **I want to** list projects the user has access to
> **So that** I can help them navigate their decisions

**Details:**
- Returns projects where user is a member
- Includes name, description, decision count

---

#### AI-2: Agent searches decisions
> **As an** AI agent
> **I want to** search decisions by query
> **So that** I can answer "what did we decide about X?"

**Details:**
- Full-text search with optional project filter
- Returns summaries, not full details (for context efficiency)

---

#### AI-3: Agent gets decision details
> **As an** AI agent
> **I want to** get full details of a specific decision
> **So that** I can provide complete context to the user

**Details:**
- Includes participants, tags, context, source info
- Used after search to dive deeper

---

#### AI-4: Agent queries by filters
> **As an** AI agent
> **I want to** query decisions with filters (project, date, author)
> **So that** I can answer specific questions

**Example queries the agent should handle:**
- "What decisions did we make last week?"
- "What has Alice decided about the backend?"
- "Show me all database-related decisions"

---

## Acceptance Criteria

### Decision Capture Criteria

| ID | Criterion |
|----|-----------|
| AC-DC-1 | @DecisionLedger mention results in stored decision within 5 seconds |
| AC-DC-2 | Bot posts confirmation with summary to same channel/thread |
| AC-DC-3 | Original message receives ✓ reaction on success |
| AC-DC-4 | Thread context captured when mention is in a thread |
| AC-DC-5 | Meeting email parsed and decisions stored within 1 minute |
| AC-DC-6 | Project auto-suggested correctly >80% of time |

### Decision Retrieval Criteria

| ID | Criterion |
|----|-----------|
| AC-DR-1 | Search returns relevant results within 500ms |
| AC-DR-2 | All filter combinations work correctly |
| AC-DR-3 | Users only see decisions from their projects |
| AC-DR-4 | Source links work for Slack messages |

### Agent Integration Criteria

| ID | Criterion |
|----|-----------|
| AC-AI-1 | Agent can answer "what did we decide about X?" with relevant decisions |
| AC-AI-2 | Agent respects user's project access |
| AC-AI-3 | API response time <500ms for agent queries |

---

## Open Questions

> **These need answers before implementation. Please provide input.**

| # | Question | Options | Impact |
|---|----------|---------|--------|
| **Q1** | Should decisions be editable after creation? | A) No, immutable<br>B) Yes, by author only<br>C) Yes, by any project member | Data integrity, audit trail |
| **Q2** | What happens if no project matches? | A) Create new project automatically<br>B) Leave unassigned (null project)<br>C) Ask user to select | UX for uncategorized decisions |
| **Q3** | Should we notify a channel when meeting decisions are ingested? | A) Yes, always<br>B) Yes, configurable per project<br>C) No | Awareness vs noise |
| **Q4** | How should the "Edit" flow work in Slack? | A) Modal dialog<br>B) Threaded message<br>C) Link to web UI | UX complexity |
| **Q5** | Should decisions have a status (active/superseded)? | A) Yes<br>B) No, just use dates | Handling changed decisions |
| **Q6** | Can users manually log decisions via slash command? | A) Yes, `/decision log <text>`<br>B) No, only @mention | Additional capture method |
| **Q7** | What meeting bot format should we support initially? | Please provide sample email | Parser implementation |

---

## Out of Scope (v1)

The following are explicitly **not** included in v1:

| Feature | Reason | Future Phase |
|---------|--------|--------------|
| Web UI for browsing | Focus on API-first, agent consumption | Phase 2 |
| Decision attachments (images, files) | Complexity | Phase 2 |
| Decision comments/discussion | Keep simple | Phase 2 |
| Audit trail / edit history | Depends on Q1 answer | TBD |
| Notifications / digests | Nice to have | Phase 2 |
| Multiple workspaces | Single workspace first | Phase 3 |
| Decision templates | Keep flexible | TBD |

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-02-03 | Aditya | Initial draft |
