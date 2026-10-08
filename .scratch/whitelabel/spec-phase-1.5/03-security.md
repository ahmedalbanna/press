# Layer 03: Security — Spec

## Problem Statement

The MCP servers and AI agent act on financial and administrative data, and they expose actions to both people and autonomous agents. Without a single, enforced security layer, an AI agent could act beyond a user's rights, sensitive data could travel in the clear, and permissions defined in Frappe could be bypassed by a direct MCP call. There is no consistent access-control contract across the three MCP servers, the agent, and the billing surface.

## Solution

Apply one security layer across every boundary: authentication (who is calling), authorization (what they may do), and encryption (how data is protected). Authentication reuses the Frappe identity system. Authorization is hybrid — Frappe permissions plus custom MCP permissions — enforced through Frappe Hooks (doc_events and custom permission checks). Encryption uses TLS in transit and AES at rest. The same contract applies to the MCP servers, the AI agent, and billing.

## User Stories

1. As an AlbannaTech customer, I want only I and my team to reach my data, so that my information stays private
2. As an AlbannaTech customer, I want my permissions in ERPNext to also apply to the AI agent, so that the assistant cannot exceed my rights
3. As an AlbannaTech customer, I want my data encrypted in transit, so that it cannot be read on the network
4. As an AlbannaTech customer, I want my data encrypted at rest, so that it cannot be read from disk
5. As an AlbannaTech customer, I want to sign in with my existing Frappe credentials, so that I have one identity everywhere
6. As an AlbannaTech customer, I want sensitive AI requests to stay local, so that my financial data does not leave the premises
7. As an AlbannaTech operator, I want a single permission model across all MCP servers, so that access is consistent
8. As an AlbannaTech operator, I want to grant per-tool, per-resource permissions, so that I can limit what each role can do
9. As an AlbannaTech operator, I want MCP permission checks enforced through Frappe Hooks, so that they cannot be bypassed by a direct call
10. As an AlbannaTech operator, I want every privileged action to be attributable to a user or agent, so that I can audit it
11. As an AlbannaTech operator, I want the agent to authenticate as the requesting user, so that its actions carry the user's rights
12. As an AlbannaTech operator, I want to revoke access centrally, so that a departed user loses access everywhere at once
13. As an AlbannaTech operator, I want subscription state to gate Advanced AI features, so that paid features are not free
14. As an AlbannaTech operator, I want encryption keys managed centrally, so that rotation is possible
15. As an AlbannaTech operator, I want security failures to fail closed, so that a broken check denies rather than allows
16. As an AlbannaTech operator, I want the billing surface to authenticate webhooks, so that forged payment notices are rejected
17. As an AlbannaTech operator, I want MCP servers to reject unauthenticated calls, so that they are not open proxies
18. As an AlbannaTech operator, I want AI agent tool calls to carry an authorization token, so that each call is checked
19. As an AlbannaTech operator, I want to log denied attempts, so that I can detect misuse
20. As an AlbannaTech operator, I want one place to change the permission rules, so that I do not edit three servers

## Implementation Decisions

### Authentication
- **Identity source**: Frappe authentication system for ERPNext/desk sessions.
- **Service-to-service**: short-lived JWT tokens secure the connection between the UI/agent and the independent MCP servers.
- **Agent calls**: the agent authenticates as the requesting user, so its actions inherit that user's rights.
- **MCP servers**: reject unauthenticated calls; every call carries a JWT.
- **Billing webhooks**: authenticated (signature verification) before any state change.

### Authorization / Access Control
- **Model**: mix — RBAC for general function permissions plus ABAC for dynamic constraints (e.g. active subscription, company/customer scope) checked at AI tool call time.
- **Mapping**: Frappe Roles decide what a user may do in ERPNext; a custom layer decides what MCP tools they may call (e.g. run Press server commands vs. only view financial reports).
- **Role hierarchy**: hierarchical (system admin → supervisor → user), so ordinary users cannot reach infrastructure tools or sensitive Press settings.
- **Team isolation**: mix — Frappe Teams/Press teams partition environments, with an MCP-layer check that prevents cross-customer data access.
- **Tool permission storage**: in Frappe, as doctypes, so permissions are managed from the normal admin UI and tied to system documents.
- **Permission propagation**: cached in Redis with a TTL for fast checks during a conversation, refreshed periodically.
- **Row-level permissions**: Frappe Permissions (User Permissions & Share) — reuse the built-in engine rather than reimplementing row filters.
- **Field-level permissions**: mix — Frappe Field Permissions hide sensitive fields from disallowed roles; critical data (payment data, integration keys) is encrypted in the database.
- **Agent permissions**: mix — the agent runs with the requesting user's permissions, under hard upper bounds ("red lines") that block dangerous operations (e.g. dropping databases, changing sensitive financial account settings) without explicit confirmation.
- **Enforcement**: Frappe Hooks (`doc_events` and custom permission checks) so permission logic lives in one place and cannot be bypassed by a direct MCP call.
- **Granularity**: per-MCP, per-tool, per-resource.
- **Fail closed**: a broken or missing check denies the action.

### Encryption
- **In transit**: TLS everywhere (Nginx terminates at the edge with SSL certificates).
- **At rest**: AES for stored data, including sensitive database fields.
- **Local-first for sensitive data**: the routing decision in layer 02 keeps sensitive requests on local models; this layer defines which data classes are sensitive.

### Session Management
- **Active sessions and caching**: Redis.
- **Stateless service auth**: JWT between services and agents.
- **Rate tracking**: Redis also tracks request rates per user.

### Key Management
- **API keys** (AI providers, payment gateways) and **encryption keys**: environment variables (`.env`) backed by Docker Secrets.
- No keys committed to the repository.

### API Protection
- **Rate limiting**: per user, to protect MCP servers and API endpoints from abuse and DDoS, and to cap AI token consumption.
- **API keys**: verification keys for service and gateway access.

### MCP Security
- **Base**: the security features of the MCP SDK.
- **Custom middleware**: a layer that verifies user identity and permissions before any tool command is executed.

### Tiering gate
- Subscription state from layer 04 is read here to gate Advanced AI features. Basic features stay available regardless.

### Auditing
- **Custom audit log** integrating Frappe logs.
- Every privileged action is attributable to a user or agent identity and logged. Denied attempts are logged distinctly.
- Tracks: every MCP tool call, every agent request, and every sensitive infrastructure or data change.

## Testing Decisions

### The seam
The seam is **permission enforcement**: attempt an action as a given identity and assert it is allowed or denied. Tests drive the system the way a caller would (with a token) and assert the outcome; they do not assert on internal permission function names.

### What makes a good test
- A test attempts a tool call as an identity without the required permission and asserts denial (fail closed).
- A test attempts the same call as an identity with the permission and asserts success.
- A test sends an unauthenticated MCP call and asserts rejection.
- A test sends a webhook with an invalid signature and asserts rejection with no state change.
- A test attempts an Advanced AI action on a Basic subscription and asserts denial.
- A test asserts that the AI agent's action is checked with the requesting user's rights, not the agent's own.
- A test attempts a cross-team resource access and asserts denial (team isolation).
- A test attempts an action above the agent's "red line" without confirmation and asserts it is blocked.
- A test asserts a row the identity may not see is absent from results, and a field they may not read is hidden.
- A test asserts a cached permission decision is refreshed after the TTL or on change.
- Tests do not assert on the hash algorithm internals or the storage format of keys.

### Which modules will be tested
- Authentication: valid, invalid, and missing credentials
- Authorization: allowed, denied, and fail-closed paths across MCP, agent, and billing
- Encryption: TLS enforced on external endpoints; at-rest encryption on stored fields
- Tiering gate: Basic vs Advanced feature access
- Audit: privileged and denied actions both recorded

### Prior art
- The Press app already overrides `has_permission` and uses `doc_events`; existing tests around those hooks show the pattern.
- Frappe's own permission tests provide the framework-level reference.

## Out of Scope

- The MCP tool implementations — layer 01.
- The agent's routing and memory — layer 02.
- Billing and subscription mechanics — layer 04 (this layer only reads subscription state).
- Hardware security modules (HSM) and key-escrow procedures.
- External penetration testing.
- Per-customer isolated key stores.

## Further Notes

- One permission model, enforced in one place (Frappe Hooks), is what makes the whole system auditable.
- Fail-closed is non-negotiable: an error in the check must deny, never allow.
- The AI agent is treated as the requesting user, never as a super-user.
