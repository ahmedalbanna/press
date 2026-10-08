# Phase 1.5 — MCP & AI Agents: Overview

This directory holds the Phase 1.5 specification, split by layer. Each layer has its own spec with its own testing seam, so each can be implemented and tested independently.

## Layers

| # | Spec | Layer | Testing Seam |
|---|------|-------|--------------|
| 01 | [MCP Servers](01-mcp-servers.md) | The three independent MCP servers (press-mcp, frappe-mcp, erpnext-mcp) | MCP tool contract |
| 02 | [AI Agent](02-ai-agent.md) | Central agent, specialized agents, memory, smart routing, hybrid models | Agent request/response contract |
| 03 | [Security](03-security.md) | Authentication, authorization, encryption, access control, permissions | Permission enforcement |
| 04 | [Billing & Subscription](04-billing.md) | Billing service, subscriptions, payment gateways | Subscription lifecycle |

## Shared Decisions (apply to every layer)

- **Language**: Python (same as Frappe)
- **Framework**: FastAPI
- **Project Structure**: Monorepo (main project + sub-projects)
- **Containerization**: Docker for every service
- **Reverse Proxy**: Nginx
- **Database**: MariaDB (same as Frappe) + Redis (sessions/queues)
- **Language Support**: Bilingual (Arabic + English), RTL/LTR
- **Platform**: Web only

## Layer Dependencies

```
01 MCP Servers  ──┐
                  ├──► 02 AI Agent (calls MCP tools)
03 Security     ──┤
                  │
04 Billing      ──┘
```

- **02 AI Agent** depends on **01 MCP Servers** (it discovers and calls their tools).
- **03 Security** applies across **01**, **02**, and **04** (enforced at every boundary).
- **04 Billing** is independent of **01** and **02**, but its subscription state gates access to Advanced AI features (checked by **03**).

## Implementation Order

1. **press-mcp** (within layer 01) — infrastructure management is the stable foundation
2. **frappe-mcp** (within layer 01) — data seeding for new customers
3. **erpnext-mcp** (within layer 01) — AI-facing operations
4. Layers 02, 03, 04 build alongside, each independently testable

## The Old Combined Spec

The original single-file spec is kept at [`../spec-phase-1.5.md`](../spec-phase-1.5.md) for reference. This directory supersedes it with a per-layer breakdown.
