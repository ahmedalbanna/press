# AlbannaTech Press Platform — Roadmap

## Phase 1.5: MCP & AI Agents (Functional Customization)

**Goal**: Implement MCP integrations and AI Agents to provide advanced functionality for customers.

**Status**: Not started

### MCP Implementation Decisions

| Decision | Choice |
|----------|--------|
| Priority | press-mcp first (all functions) |
| Code Location | press-mcp in Press + erpnext-mcp in ERPNext |
| Deployment | On Press server (central management) |
| MCP Server Type | Independent server (each MCP as separate service) |
| Language | Python (same as Frappe) |
| Framework | FastAPI (modern, async, auto-docs) |
| MCP Library | Official MCP SDK |
| Database | MariaDB (same as Frappe) + Redis (sessions) |
| Containerization | Docker for each MCP server |
| Reverse Proxy | Nginx |
| Project Structure | Monorepo (main project + sub-projects) |
| AI Agent Integration | Via MCP SDK |
| AI Agent Framework | LangChain (or lightweight LLM tool calling) |
| NLP Library | Transformers |
| Data Processing | Pandas |
| Local Models | Ollama via Docker (isolated, easy deployment) |
| Cloud Providers | Unified API (OpenAI, Gemini, Anthropic) |
| Hybrid AI Routing | Smart (automatic based on task complexity) |
| AI Agent Architecture | Hybrid (central agent + specialized agents) |
| AI Agent Communication | Via MCP protocol |
| MCP Communication | Mix (REST API for sync + Redis for async) |
| AI Agent UI | Frappe UI chat sidebar in ERPNext Desk |
| press-mcp UI | CLI + simple dashboard |
| erpnext-mcp UI | Chat sidebar in ERPNext |
| AI Agent Language | Bilingual (Arabic + English) |
| AI Agent Platform | Web only (ERPNext chat sidebar) |
| Pricing Model | Basic: free with hosting, Advanced: paid annual |

### Interface Technology

| Decision | Choice |
|----------|--------|
| Chat Sidebar | Custom Vue component on Frappe UI (matches desk design system) |
| Packaging | Custom Frappe App (installed/updated via Bench) |
| Standalone Page | Custom Frappe Page inside ERPNext |
| Real-time Streaming | WebSocket / Server-Sent Events (token streaming) |
| Chat Rendering | Markdown + interactive elements (tables, code, action buttons) |
| Quick Actions | Mix (ready buttons + slash commands + auto-suggestions) |
| RTL Support | Mix (`dir` attribute + CSS logical properties + Tailwind RTL) |
| i18n | Frappe Translation system |

### Access Control & Permissions

| Decision | Choice |
|----------|--------|
| Access Control | Hybrid (Frappe system + custom MCP permissions) |
| Permissions Integration | Frappe Hooks (doc_events, custom permissions) |
| Authentication | Mix (Frappe Auth for desk + short-lived JWT for MCP services) |
| Authorization | Mix (Frappe Roles + custom RBAC for MCP tools) |
| Encryption | TLS in transit + AES at rest (sensitive fields encrypted) |
| Session Management | Mix (Redis for active sessions/cache + JWT stateless) |
| Key Management | Environment variables (.env) backed by Docker Secrets |
| Audit Logging | Custom audit log integrating Frappe logs |
| API Protection | Rate limiting (per user) + API keys |
| MCP Security | MCP SDK + custom middleware (verify identity/permissions before tool execution) |

### Phase 1.5 Per-Layer Specs

| Layer | Spec | Testing Seam |
|-------|------|--------------|
| MCP Servers | `.scratch/whitelabel/spec-phase-1.5/01-mcp-servers.md` | MCP tool contract |
| AI Agent | `.scratch/whitelabel/spec-phase-1.5/02-ai-agent.md` | Agent request/response contract |
| Security | `.scratch/whitelabel/spec-phase-1.5/03-security.md` | Permission enforcement |
| Billing & Subscription | `.scratch/whitelabel/spec-phase-1.5/04-billing.md` | Subscription lifecycle |

### Billing & Subscription

| Decision | Choice |
|----------|--------|
| Billing Service | Hybrid (Press for hosting + custom layer for AI subscriptions/tokens) |
| Invoices | Frappe Invoice doctype |
| Subscription | Frappe Subscription doctype (built-in periodic renewal) |
| Usage Metering | Redis (real-time) synced to MariaDB (durable) |
| Taxes | Frappe Tax Templates |
| Currencies | Multiple (USD + SAR, matching gateways) |
| Financial Reports | Frappe Reports |
| Press Integration | Mix (REST for requests + webhook for async events) |
| Payment Gateway | Mix (HyperPay + PayTabs) |
| Payment Gateway Integration | Webhook |

### AI Agent Architecture

| Decision | Choice |
|----------|--------|
| Central Agent | Central agent + router (receives requests, routes to specialized agents) |
| Specialized Agents | Mix — agent per MCP + agents per function |
| Memory | Mix — short-term (conversation context) + long-term (preferences, history) |
| Smart Routing | Mix — text analysis + task type + data size |
| Local Models | Multiple models (lightweight for chat/extraction, specialized for structural tasks) |
| Cloud Models | Mix — primary provider + backup provider (Gemini ↔ OpenAI) |
| UI | Mix — chat sidebar (daily ops) + independent page (settings, analytics) |
| Security | Authentication + authorization + encryption (Frappe permissions + data encryption) |
| Language | Bilingual (Arabic + English) |
| Platform | Web only |

### AI Agent Functions by MCP

#### press-mcp AI Agent
- Problem diagnosis (log analysis, solutions)
- Resource management (automatic allocation)
- Smart alerts (proactive notifications)
- CLI assistance (command writing help)

#### frappe-mcp AI Agent
- Data analysis (client data analysis)
- Automatic data entry (from files)
- Data validation (accuracy checks)
- Structuring suggestions (recommendations)

#### erpnext-mcp AI Agent
- Data entry (invoices, purchase orders, customers)
- Reports (financial and administrative)
- Conversation (inventory, sales, accounting questions)
- Automation (repetitive processes, anomaly detection)

### Pricing Tiers
- **Basic Agent**: Free with hosting — daily operations, simple data entry, FAQs, ready reports
- **Advanced Pro Agent**: Paid annual — complex financial analysis, advanced automation, operational predictions

### Implementation Order
1. **press-mcp** — Infrastructure management, site management, version management, support
2. **frappe-mcp** — Data seeding for new customers
3. **erpnext-mcp** — AI Agents with hybrid architecture (Ollama + Cloud)

### Key Deliverables
- press-mcp integrated for infrastructure management
- frappe-mcp for automated data seeding
- erpnext-mcp AI Agent with chat sidebar in ERPNext
- Hybrid AI architecture (local Ollama + cloud Gemini/OpenAI)
- Bilingual AI Agent (Arabic + English)
- Two-tier pricing model (Basic free, Advanced paid)

---

## Phase 1: White-Label Rebranding (Current)

**Goal**: Rebrand the Press platform across all customer-facing surfaces to AlbannaTech's visual identity.

**Status**: In progress

### Original Tickets

| # | Title | Status | Blocked by |
|---|-------|--------|------------|
| 01 | Foundation — Brand Assets & CSS Variables | Ready | None |
| 02 | Dashboard Rebranding | Ready | 01 |
| 03 | Signup & Login Rebranding | Ready | 01 |
| 04 | Email Template Rebranding | Ready | 01 |
| 05 | Marketplace Rebranding | Ready | 01 |
| 06 | Bilingual Support (Arabic/English) | Ready | 02, 03, 04, 05 |

### New Tickets (Added)

| # | Title | Status | Blocked by |
|---|-------|--------|------------|
| 07 | Landing Page | Ready | 01 |
| 08 | Documentation Site | Ready | 01 |
| 09 | FAQ Page | Ready | 01 |
| 10 | Pricing Page | Ready | 01 |
| 11 | Blog | Ready | 01 |
| 12 | Visual Identity Comprehensive Review | Ready | 02, 03, 04, 05 |
| 13 | Visual Regression Tests | Ready | 02, 03 |
| 14 | Performance Measurement | Ready | 02 |
| 15 | Cross-Browser Compatibility Tests | Ready | 02, 03 |

### Key Deliverables
- AlbannaTech logo and favicon deployed to all surfaces
- Brand colors (#0F172A, #0EA5E9, #10B981) applied throughout
- Bilingual support (Arabic/English) with RTL/LTR
- All Frappe Cloud references replaced with AlbannaTech equivalents
- Landing page, documentation, FAQ, pricing, and blog pages
- Visual identity review complete with checklist
- Visual regression tests passing
- Performance baseline measured
- Cross-browser compatibility verified

---

## Phase 2: Production Readiness

**Goal**: Prepare the platform for production launch with focus on stability, security, and payment processing.

**Status**: Not started

### Infrastructure Decisions

| Decision | Choice |
|----------|--------|
| Server Type | On-Premise (office server) |
| OS | Ubuntu Server 22.04 LTS |
| Server Specs | 2 vCPU, 4GB RAM, 80GB SSD (3-5 customers) |
| Static IP | Request from ISP |
| Containerization | Docker |
| Setup Method | Manual (no Ansible playbooks) |
| Budget | <$100/month |

### Domain & DNS Decisions

| Decision | Choice |
|----------|--------|
| Domain Registrar | Cloudflare |
| DNS | Cloudflare (free) |
| CDN | Cloudflare (free) |
| DDoS Protection | Cloudflare (basic, free) |
| SSL | Let's Encrypt (auto-renewing) |

### Payment Decisions

| Decision | Choice |
|----------|--------|
| Payment Gateway | Arabic gateway (HyperPay or PayTabs) |
| Model | Paid cloud hosting |

### Email Decisions

| Decision | Choice |
|----------|--------|
| SMTP | SendGrid (100 emails/day free) |

### Security Decisions

| Decision | Choice |
|----------|--------|
| Brute Force Protection | Fail2ban |
| Firewall | UFW (Uncomplicated Firewall) |
| 2FA | Built-in Press 2FA |

### Monitoring Decisions

| Decision | Choice |
|----------|--------|
| Monitoring Level | Basics (CPU, RAM) |
| Tools | Built-in Linux tools (htop, vmstat, iostat) |

### Workstreams

#### 2.1 Server Setup
- [ ] Request static IP from ISP
- [ ] Purchase domain (albannatech.com or similar)
- [ ] Install Ubuntu Server 22.04 LTS
- [ ] Configure network and firewall (UFW)
- [ ] Install Docker and Docker Compose
- [ ] Install Fail2ban
- [ ] Configure automatic security updates

#### 2.2 Platform Deployment
- [ ] Deploy Press platform via Docker
- [ ] Configure Nginx as reverse proxy
- [ ] Set up Let's Encrypt SSL certificates
- [ ] Configure Cloudflare DNS and CDN
- [ ] Test platform accessibility from internet

#### 2.3 Payment Integration
- [ ] Set up HyperPay or PayTabs account
- [ ] Configure payment gateway in Press
- [ ] Test payment flow end-to-end
- [ ] Set up automatic invoicing
- [ ] Configure subscription management

#### 2.4 Email Setup
- [ ] Create SendGrid account
- [ ] Verify domain with SendGrid
- [ ] Configure SMTP in Press
- [ ] Test email delivery
- [ ] Set up email templates with AlbannaTech branding

#### 2.5 Backup & Recovery
- [ ] Set up daily database backups
- [ ] Set up weekly file backups
- [ ] Test backup restoration
- [ ] Document recovery procedures

#### 2.6 Monitoring & Alerting
- [ ] Set up CPU and RAM monitoring
- [ ] Configure disk space alerts
- [ ] Set up uptime monitoring
- [ ] Create basic health check dashboard

#### 2.7 Security Hardening
- [ ] Configure Fail2ban rules
- [ ] Set up UFW firewall rules
- [ ] Disable root SSH login
- [ ] Set up SSH key authentication
- [ ] Configure automatic security updates
- [ ] Run security vulnerability scan

### Key Deliverables
- Server running Ubuntu 22.04 with Docker
- Platform accessible via domain with SSL
- Payment gateway operational
- Email delivery working
- Backup system operational
- Basic monitoring active
- Security hardening complete

---

## Phase 3: Launch & Customer Acquisition

**Goal**: Launch the platform and acquire first customers.

**Status**: Not started

### Business Decisions

| Decision | Choice |
|----------|--------|
| Target Audience | Small companies (1-50 employees) |
| Marketing Strategy | Partner marketing with consulting companies |
| Support Team | 1-2 people (partial) |
| Pricing Model | Usage-based (per transaction) |
| Communication Channel | Phone (direct number) |
| Partner Count | Start with 1-2 partners |
| Revenue Split | 60/40 (60% us, 40% partner) |
| Support Request Method | Website form |
| Response Time | Based on priority |
| Knowledge Base | Yes, comprehensive with FAQs and guides |

### Workstreams

#### 3.1 Pre-Launch
- [ ] Beta testing with internal team
- [ ] Bug fixes from beta feedback
- [ ] Performance optimization based on beta metrics
- [ ] Documentation review
- [ ] Support process definition
- [ ] Create knowledge base with FAQs and guides
- [ ] Set up website contact form
- [ ] Define support priority levels and response times

#### 3.2 Launch
- [ ] Production deployment
- [ ] DNS cutover
- [ ] SSL certificate activation
- [ ] SMTP verification
- [ ] Payment gateway testing in production
- [ ] Monitoring dashboard active
- [ ] Set up phone number and call routing
- [ ] Test support form end-to-end

#### 3.3 Post-Launch
- [ ] Customer onboarding process
- [ ] Support ticket system
- [ ] Customer feedback collection
- [ ] Performance monitoring
- [ ] Regular security updates
- [ ] Monitor partner relationships
- [ ] Track transaction-based usage for billing

#### 3.4 Marketing & Sales
- [ ] Landing page creation
- [ ] Documentation site
- [ ] Pricing page (transaction-based)
- [ ] Blog/content strategy
- [ ] Social media presence
- [ ] Partner program setup
- [ ] Partner outreach to consulting companies
- [ ] Partner agreement templates
- [ ] Partner portal or dashboard

### Key Deliverables
- Platform live and accessible to customers
- First paying customers onboarded
- Support process operational
- Marketing materials ready
- Knowledge base live
- Partner program launched
- Phone support operational
- Transaction-based billing system working

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1 | 2-3 weeks | None |
| Phase 2 | 6-8 weeks | Phase 1 complete |
| Phase 3 | 2-3 weeks | Phase 2 complete |
| **Total** | **10-14 weeks** | |

---

## Success Metrics

### Phase 1
- All 6 original tickets completed
- All 9 new tickets completed
- Zero Frappe Cloud references in customer-facing surfaces
- Bilingual support working correctly
- Visual regression tests passing
- Cross-browser compatibility verified

### Phase 2
- Page load time < 2 seconds
- API response time < 500ms
- Zero critical security vulnerabilities
- Payment processing success rate > 99%
- Backup restoration tested and working

### Phase 3
- First 10 customers onboarded
- Zero critical bugs in production
- Customer satisfaction score > 4/5

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Static IP delays from ISP | High | Request early, have backup plan (dynamic DNS) |
| On-premise power/network outages | High | UPS for power, backup internet connection |
| Payment gateway approval delays | High | Start application early, have alternative ready |
| Security breach | High | Regular audits, Fail2ban, automatic updates |
| Scope creep | Medium | Strict phase boundaries |
| Single point of failure (one server) | Medium | Document recovery plan, consider backup server later |

---

## Notes

- Phase 1 tickets are ready for implementation
- Phase 2 should be reviewed with another agent before starting
- Phase 3 timing depends on Phase 2 completion
- All phases should be documented as they progress
- On-premise server requires physical access for maintenance
- Consider cloud backup for on-premise server data
