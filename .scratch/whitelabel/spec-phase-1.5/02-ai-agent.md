# Layer 02: AI Agent — Spec

## Problem Statement

Customers and AlbannaTech operators need an AI assistant that can act inside ERPNext and across the MCP servers. A single monolithic model is both too costly (every request goes to a paid cloud API) and too risky (sensitive financial data leaving the premises). There is also no memory: every question starts from zero, and no routing: simple questions cost the same as deep analysis.

## Solution

Build a central AI agent with a router and a set of specialized agents. The central agent classifies each request and routes it to the right specialized agent and the right model: local models (Ollama) for simple, fast, or sensitive work, and cloud models (Gemini/OpenAI) for complex analysis. A memory system keeps short-term conversation context (Redis) and long-term preferences and history (MariaDB). The agent calls MCP tools (layer 01) to act, and exposes a chat sidebar in ERPNext plus a standalone management page.

## User Stories

1. As an AlbannaTech customer, I want to ask questions in natural language and get answers, so that I do not need to learn ERPNext screens
2. As an AlbannaTech customer, I want the assistant to create an invoice from a sentence, so that data entry is fast
3. As an AlbannaTech customer, I want the assistant to generate a financial report on request, so that I get instant insight
4. As an AlbannaTech customer, I want the assistant to answer inventory, sales, and accounting questions, so that I can make decisions quickly
5. As an AlbannaTech customer, I want the assistant to run a repetitive process for me, so that I save time
6. As an AlbannaTech customer, I want the assistant to flag anomalies, so that I catch problems early
7. As an AlbannaTech customer, I want the assistant to remember my preferences, so that I do not repeat myself
8. As an AlbannaTech customer, I want the assistant to remember our conversation, so that follow-up questions work
9. As an AlbannaTech customer, I want a chat sidebar in ERPNext, so that help is one click away
10. As an AlbannaTech customer, I want a standalone page for agent settings and analytics, so that I can control and monitor it
11. As an AlbannaTech customer, I want to talk to the assistant in Arabic or English, so that I use my preferred language
12. As an AlbannaTech customer, I want sensitive questions answered by a local model, so that my data stays private
13. As an AlbannaTech customer, I want complex analysis handled by a cloud model, so that I get the best answer
14. As an AlbannaTech customer, I want the assistant to keep working when one cloud provider is down, so that I am not blocked
15. As an AlbannaTech customer, I want the Basic agent for free with hosting, so that I get everyday help at no cost
16. As an AlbannaTech customer, I want the Advanced Pro agent as a paid upgrade, so that I can access premium analysis
17. As an AlbannaTech operator, I want the router to be configurable, so that I can tune cost versus quality
18. As an AlbannaTech operator, I want to see which model served each request, so that I can audit cost and quality
19. As an AlbannaTech operator, I want the agent to fail over between providers, so that availability stays high
20. As an AlbannaTech operator, I want the agent to respect permissions, so that it never acts beyond a user's rights

## Implementation Decisions

### Agent topology
- **Central agent + router**: one entry point that classifies intent and routes.
- **Specialized agents**: a mix of agent-per-MCP (infrastructure, data seeding, ERPNext) and agent-per-function (reports, data entry, conversation). The central agent picks the appropriate one.
- **Acting**: specialized agents act by calling MCP tools from layer 01 through the MCP SDK.

### Memory
- **Short-term**: Redis — the current conversation context for the sidebar.
- **Long-term**: MariaDB — customer preferences, past operations, and history retrieved when relevant.

### Smart routing
- **Inputs to the decision**: text complexity, task type (data entry, report, conversation, analysis), and data size.
- **Local path (Ollama, Docker)**: simple, routine, and sensitive requests. Multiple local models: a lightweight one for chat and extraction, a specialized one for structural tasks.
- **Cloud path**: complex analytical work. Unified API across providers.
- **Failover**: a primary cloud provider with a backup (Gemini ↔ OpenAI), switched automatically.

### Interface
- **Chat sidebar**: Frappe UI floating sidebar in ERPNext Desk for daily operations.
- **Standalone page**: agent settings and analytics.
- **Language**: bilingual (Arabic + English), RTL/LTR.
- **Platform**: web only.

### Libraries
- **Agent framework**: LangChain, or a lightweight structure built directly on modern LLM tool calling.
- **NLP**: Transformers for local embeddings and light semantic processing.
- **Data processing**: Pandas for tabular work, financial reports, and ERPNext data transformation.

### Tiering
- **Basic agent**: free with hosting — daily operations, simple data entry, FAQs, ready reports.
- **Advanced Pro agent**: paid annual — complex financial analysis, advanced automation, operational predictions. Access is gated by layer 03 against subscription state from layer 04.

## Testing Decisions

### The seam
The seam is the **agent request/response contract**: send a request (text, user context, language) and assert on the structured response (answer, which agent handled it, which model served it, which tools were called). Tests do not assert on prompt text or internal chain steps. This is the highest seam that still exercises routing, memory, and tool-calling.

### What makes a good test
- A test sends a request and asserts the response names the correct specialized agent and model tier (local vs cloud).
- A test sends a follow-up and asserts long-term memory is applied (preference respected).
- A test simulates a cloud provider failure and asserts failover to the backup provider.
- A test sends a request that requires an MCP tool and asserts the tool was invoked and its result shaped the answer.
- Tests use mock LLM responses so routing and memory are deterministic and do not depend on a live model.
- Tests do not assert on exact wording of the model's prose.

### Which modules will be tested
- Intent classification and routing (local vs cloud, which specialized agent)
- Memory: short-term context retention and long-term preference recall
- Failover: primary → backup provider
- Tool invocation: correct MCP tool called with correct arguments
- Tiering: Basic vs Advanced gating
- Bilingual handling: Arabic and English requests both route and respond

### Prior art
- Existing Playwright UI tests in `dashboard/tests-e2e/` show the pattern for testing the sidebar interaction end to end.
- Deterministic mock-based tests follow the existing Python test conventions in `press/tests/`.

## Out of Scope

- The MCP tool implementations themselves — that is layer 01.
- Authentication, authorization, and encryption internals — that is layer 03 (the agent consumes them).
- Billing and subscription mechanics — that is layer 04 (the agent reads subscription state).
- Training or fine-tuning custom models.
- Voice interfaces and non-web clients.
- A marketplace of third-party agents.

## Further Notes

- The hybrid architecture is the core cost and privacy control: sensitive stays local, complex goes to cloud.
- Routing must be configurable so operators can trade cost against quality without code changes.
- The agent is bilingual from the ground up, including RTL layout in the sidebar.
