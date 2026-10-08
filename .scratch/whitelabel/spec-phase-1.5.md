# Phase 1.5: MCP & AI Agents — Spec

## Problem Statement

AlbannaTech needs to implement three MCP (Model Context Protocol) servers and AI Agents to provide advanced functionality for their hosting platform. The goal is to enable infrastructure management (press-mcp), automated data seeding (frappe-mcp), and AI-powered daily operations (erpnext-mcp). These systems will be deployed on the Press server as independent services, using a hybrid AI architecture that combines local models (Ollama) for simple/sensitive tasks with cloud models (Gemini/OpenAI) for complex analytical tasks.

## Solution

Implement three independent MCP servers in a monorepo structure, each with its own AI Agent capabilities. The system uses a central AI agent with a router that directs requests to specialized agents based on task complexity, type, and data size. The hybrid AI architecture ensures optimal performance, cost-efficiency, and data security. All services are containerized with Docker, proxied through Nginx, and integrated with the existing Frappe/ERPNext ecosystem.

## User Stories

1. As an AlbannaTech system administrator, I want to manage servers, sites, and versions through press-mcp, so that I can efficiently manage customer hosting infrastructure
2. As an AlbannaTech system administrator, I want AI-assisted problem diagnosis through press-mcp, so that I can quickly identify and resolve infrastructure issues
3. As an AlbannaTech system administrator, I want AI-assisted resource management through press-mcp, so that resources are allocated optimally across customer sites
4. As an AlbannaTech system administrator, I want proactive smart alerts through press-mcp, so that I can address issues before they impact customers
5. As an AlbannaTech system administrator, I want CLI assistance through press-mcp, so that I can write correct commands quickly
6. As an AlbannaTech customer, I want automated data seeding through frappe-mcp, so that my system is ready to use immediately after subscription
7. As an AlbannaTech customer, I want AI-assisted data analysis through frappe-mcp, so that my data is structured optimally for my business needs
8. As an AlbannaTech customer, I want automatic data entry through frappe-mcp, so that I can import data from files without manual input
9. As an AlbannaTech customer, I want data validation through frappe-mcp, so that my data is accurate and consistent
10. As an AlbannaTech customer, I want data structuring suggestions through frappe-mcp, so that my data model follows best practices
11. As an AlbannaTech customer, I want AI-assisted data entry through erpnext-mcp, so that I can create invoices, purchase orders, and customer records using natural language
12. As an AlbannaTech customer, I want AI-generated financial reports through erpnext-mcp, so that I can get instant insights without manual report building
13. As an AlbannaTech customer, I want conversational AI through erpnext-mcp, so that I can ask questions about inventory, sales, and accounting in natural language
14. As an AlbannaTech customer, I want AI-powered automation through erpnext-mcp, so that repetitive processes are handled automatically
15. As an AlbannaTech customer, I want anomaly detection through erpnext-mcp, so that financial and operational irregularities are flagged immediately
16. As an AlbannaTech customer, I want a chat sidebar in ERPNext, so that I can access AI assistance without leaving my workflow
17. As an AlbannaTech customer, I want a standalone AI management page, so that I can configure agent settings and view analytics
18. As an AlbannaTech customer, I want bilingual AI support (Arabic + English), so that I can interact in my preferred language
19. As an AlbannaTech customer, I want the AI to use local models for sensitive data, so that my financial data remains private
20. As an AlbannaTech customer, I want the AI to use cloud models for complex analysis, so that I get the most accurate insights
21. As an AlbannaTech customer, I want the Basic AI Agent to be free with hosting, so that I can use AI assistance without additional cost
22. As an AlbannaTech customer, I want the Advanced Pro AI Agent as a paid annual subscription, so that I can access premium AI capabilities
23. As an AlbannaTech customer, I want my AI interactions to be secure, so that my data is protected with authentication, authorization, and encryption
24. As an AlbannaTech customer, I want the AI to remember my preferences, so that I don't have to repeat context in every conversation
25. As an AlbannaTech customer, I want the AI to have conversation memory, so that it can reference previous interactions

## Implementation Decisions

### MCP Server Architecture
- **Language**: Python (same as Frappe framework)
- **Framework**: FastAPI (modern, async, auto-generated API docs)
- **MCP Library**: Official MCP SDK for protocol compliance
- **Project Structure**: Monorepo with main project + sub-projects for each MCP
- **Deployment**: Independent Docker containers for each MCP server
- **Reverse Proxy**: Nginx for routing, SSL termination, and backend protection
- **Database**: MariaDB (same as Frappe) + Redis for session management

### MCP Communication
- **Inter-MCP**: REST API for synchronous requests + Redis message queue for async operations
- **Agent-to-MCP**: Via MCP protocol (official SDK)
- **Tool Discovery**: Dynamic tool discovery through MCP SDK

### AI Agent Architecture
- **Central Agent**: Central agent + router that receives requests and routes to specialized agents
- **Specialized Agents**: Mix of agent-per-MCP + agent-per-function
- **Memory System**: Short-term memory (Redis, conversation context) + long-term memory (MariaDB, preferences, history)
- **Smart Routing**: Text analysis + task type classification + data size analysis
- **AI Framework**: LangChain (or lightweight structure based on modern LLM tool calling)
- **NLP Library**: Transformers (for local embeddings and semantic processing)
- **Data Processing**: Pandas (for table processing, financial reports, ERPNext data transformation)

### Hybrid AI Architecture
- **Local Models**: Ollama via Docker (multiple models: lightweight for chat/extraction, specialized for structural tasks)
- **Cloud Models**: Primary provider (Gemini) + backup provider (OpenAI) with unified API interface
- **Routing Logic**: Automatic based on task complexity, data sensitivity, and size
- **Data Security**: Sensitive data stays local, complex analysis goes to cloud

### AI Agent Security
- **Authentication**: Frappe authentication system
- **Authorization**: Frappe permissions + custom MCP permissions
- **Encryption**: TLS for data in transit, AES for data at rest
- **Integration**: Frappe Hooks (doc_events) for permission enforcement

### Access Control
- **System**: Hybrid (Frappe system + custom MCP permissions)
- **Integration**: Frappe Hooks (doc_events, custom permission checks)
- **Granularity**: Per-MCP, per-tool, per-resource

### Billing & Subscription
- **Billing Service**: Hybrid (Press system + custom billing service)
- **Billing Integration**: REST API
- **Subscription**: Hybrid (Press system + custom subscriptions)
- **Subscription Integration**: REST API
- **Payment Gateway**: HyperPay + PayTabs
- **Payment Gateway Integration**: Webhook for payment notifications

### AI Agent UI
- **Chat Sidebar**: Frappe UI floating sidebar in ERPNext Desk for daily operations
- **Standalone Page**: Independent page in dashboard for agent settings and analytics
- **Language**: Bilingual (Arabic + English) with RTL/LTR support
- **Platform**: Web only

### Pricing Model
- **Basic Agent**: Free with hosting — daily operations, simple data entry, FAQs, ready reports
- **Advanced Pro Agent**: Paid annual subscription — complex financial analysis, advanced automation, operational predictions

### Implementation Order
1. **press-mcp** — Infrastructure management, site management, version management, support
2. **frappe-mcp** — Data seeding for new customers
3. **erpnext-mcp** — AI Agents with hybrid architecture

## Testing Decisions

### What makes a good test
- Tests verify external behavior: what the user sees and experiences
- Tests do not verify implementation details: specific code structure, internal APIs
- Tests check that MCP tools are discoverable and callable
- Tests verify AI Agent responses are accurate and relevant
- Tests verify security controls are enforced
- Tests verify billing and subscription logic works correctly

### Which modules will be tested
- **MCP Server**: Tool discovery, tool execution, error handling
- **AI Agent**: Intent classification, routing, response generation
- **Hybrid AI**: Local/cloud routing, model fallback
- **Security**: Authentication, authorization, encryption
- **Billing**: Invoice generation, subscription management, payment processing
- **UI**: Chat sidebar, standalone page, bilingual support

### Prior art
- The Press app has existing tests in `press/tests/` for doctype logic
- UI tests exist in `dashboard/tests-e2e/` using Playwright
- MCP tests can follow the pattern of existing API tests
- AI Agent tests can use mock LLM responses for deterministic testing

## Out of Scope

- **Mobile applications**: iOS and Android apps — web only for now
- **Voice interface**: Voice-based AI interaction — text only for now
- **Multi-tenant AI**: Separate AI models per customer — shared infrastructure for now
- **Custom model training**: Training custom models on customer data — pre-trained models only for now
- **AI Agent marketplace**: Third-party AI agents — AlbannaTech agents only for now
- **Advanced analytics**: Predictive analytics and forecasting — basic reporting for now
- **Integration with external AI services**: Third-party AI services — AlbannaTech infrastructure only for now

## Further Notes

- The monorepo structure allows sharing common libraries (auth, MCP utils, AI utils) while maintaining service independence
- The hybrid AI architecture ensures data privacy for sensitive financial data while leveraging cloud capabilities for complex analysis
- The two-tier pricing model (Basic free, Advanced paid) provides a clear upgrade path for customers
- All MCP servers are containerized with Docker for easy deployment and scaling
- The system is designed to be bilingual (Arabic + English) from the ground up
- Security is a core concern: authentication, authorization, and encryption are implemented at every layer
- The implementation order (press-mcp → frappe-mcp → erpnext-mcp) ensures infrastructure is stable before adding customer-facing features
