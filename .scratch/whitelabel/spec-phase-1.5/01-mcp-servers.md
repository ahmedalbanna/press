# Layer 01: MCP Servers — Spec

## Problem Statement

AlbannaTech needs three separate services that expose their capabilities through the Model Context Protocol (MCP), so that both human operators and AI agents can manage infrastructure, seed customer data, and operate ERPNext through a single, discoverable tool contract. Today there is no such contract: infrastructure, data seeding, and ERPNext operations are performed through bespoke scripts and manual steps, which cannot be discovered or called by an AI agent.

## Solution

Build three independent MCP servers, each deployed as its own Docker container behind Nginx, each exposing its own set of MCP tools:

- **press-mcp** — infrastructure management (servers, sites, versions, support/diagnostics)
- **frappe-mcp** — data seeding for new customers (analysis, import, validation, structuring)
- **erpnext-mcp** — ERPNext operations (data entry, reports, conversation, automation, anomaly detection)

They live in one monorepo so they can share common libraries (auth, JSON-RPC handling, tool registration) while remaining independently deployable. Servers talk to each other over REST for synchronous calls and Redis for asynchronous work.

## User Stories

1. As an AI agent, I want to discover the tools each MCP server exposes, so that I can call the right tool without hard-coded knowledge
2. As an AI agent, I want to call a press-mcp tool to list servers, so that I can answer infrastructure questions
3. As an AI agent, I want to call a press-mcp tool to create or update a site, so that I can act on infrastructure requests
4. As an AI agent, I want to call a press-mcp tool to diagnose a failing server, so that I can surface the cause
5. As an AI agent, I want to call a press-mcp tool to allocate resources, so that resources are distributed optimally
6. As an AI agent, I want to call a press-mcp tool to raise a proactive alert, so that issues are caught before customers feel them
7. As an AI agent, I want to call a frappe-mcp tool to analyse a customer's data, so that I can propose a structure
8. As an AI agent, I want to call a frappe-mcp tool to import data from a file, so that a new customer's system is populated
9. As an AI agent, I want to call a frappe-mcp tool to validate imported data, so that inconsistencies are caught before they spread
10. As an AI agent, I want to call a frappe-mcp tool to suggest a data structure, so that the customer's model follows best practices
11. As an AI agent, I want to call an erpnext-mcp tool to create an invoice, purchase order, or customer, so that data entry happens from natural language
12. As an AI agent, I want to call an erpnext-mcp tool to generate a financial report, so that the user gets an instant answer
13. As an AI agent, I want to call an erpnext-mcp tool to query inventory, sales, and accounting, so that conversational questions are answered
14. As an AI agent, I want to call an erpnext-mcp tool to run a repetitive process, so that automation is triggered
15. As an AI agent, I want to call an erpnext-mcp tool to detect anomalies, so that irregularities are flagged
16. As an AlbannaTech operator, I want each MCP server to fail independently, so that one broken service does not take down the others
17. As an AlbannaTech operator, I want each MCP server to expose its tools with typed inputs and outputs, so that calls are predictable
18. As an AlbannaTech operator, I want MCP servers to communicate asynchronously for heavy work, so that slow operations do not block callers
19. As an AlbannaTech operator, I want the same authentication contract across all three servers, so that access is consistent
20. As an AlbannaTech operator, I want the monorepo to share common libraries, so that fixes propagate to all servers

## Implementation Decisions

### Structure
- **Monorepo**: one repository, one sub-project per server (`press-mcp`, `frappe-mcp`, `erpnext-mcp`), plus a `shared/` library for auth, MCP/JSON-RPC helpers, and AI utilities.
- **Independent services**: each server builds its own Docker image and runs its own container; no shared process.
- **Independent failure**: each container has its own health check; Nginx routes to each independently.

### Technology
- **Language**: Python.
- **Framework**: FastAPI (async, auto-generated OpenAPI docs).
- **MCP**: official MCP SDK; every tool is registered through the SDK so discovery is automatic.
- **Database**: MariaDB (same instance family as Frappe) for durable state; Redis for sessions and async queues.
- **Deployment**: Docker per server, Nginx as reverse proxy with SSL termination.

### Communication
- **Inter-MCP, synchronous**: REST calls between servers.
- **Inter-MCP, asynchronous**: Redis-backed queue for heavy or long-running operations.
- **Tool contract**: MCP protocol; every tool declares its name, description, input schema, and output schema.

### press-mcp Tools (infrastructure)
- Servers: list, inspect, create, update, delete
- Sites: list, inspect, create, backup, restore, update
- Versions: list apps, list releases, update app/release
- Support: diagnose, tail logs, raise alert, allocate resource

### frappe-mcp Tools (data seeding)
- Analyse customer data
- Import data from file
- Validate imported data
- Suggest data structure

### erpnext-mcp Tools (operations)
- Data entry: invoice, purchase order, customer
- Reports: financial, administrative
- Conversation: query inventory, sales, accounting
- Automation: run repetitive process
- Anomaly detection: flag irregular financial/operational events

### Implementation Order
1. **press-mcp** — stable infrastructure foundation
2. **frappe-mcp** — data seeding
3. **erpnext-mcp** — AI-facing operations

## Testing Decisions

### The seam
The seam is the **MCP tool contract** — the protocol boundary. Tests call tools through the MCP SDK the same way an agent would, and assert on the tool's typed output. They never reach into the server's internals. This is the highest possible seam: one contract per server covers discovery, execution, and error handling.

### What makes a good test
- A test registers a tool, calls it through MCP with valid input, and asserts on the structured output.
- A test calls a tool with invalid input and asserts a typed, protocol-level error (not a stack trace).
- A test lists tools and asserts the expected tools are discoverable with valid schemas.
- Tests do not assert on internal function names, database rows, or HTTP routes.

### Which modules will be tested
- Tool discovery for each server
- Tool execution for each server (one test per tool at minimum)
- Error handling: invalid input, missing resource, upstream failure
- Async path: a heavy operation enqueues and completes via Redis
- Cross-server REST call: one server calls another and gets a typed result

### Prior art
- Existing API tests in `press/tests/` show the pattern of calling a whitelisted method and asserting on the result.
- The MCP SDK's own test client is the natural driver, mirroring how an agent calls the server.

## Out of Scope

- The AI logic that decides *which* tool to call — that is layer 02.
- Authentication and permission enforcement — that is layer 03.
- Billing and subscription state — that is layer 04.
- Multi-tenant isolation of MCP servers (separate instance per customer).
- A public/third-party MCP marketplace.
- Non-web clients (mobile, desktop, voice).

## Further Notes

- Keeping every server in one monorepo but one container each gives shared code with independent failure.
- The MCP contract is the single stable interface; internal implementation may change freely behind it.
- press-mcp is built first because the other two lean on a stable infrastructure foundation.
