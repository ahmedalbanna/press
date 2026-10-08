# Layer 04: Billing & Subscription — Spec

## Problem Statement

AlbannaTech sells two things: managed hosting and an Advanced Pro AI agent subscription. Today there is no service that turns a customer's usage and plan into an invoice, tracks subscription state, and accepts payment. Without it, Advanced AI features cannot be gated, revenue cannot be collected, and the free Basic tier cannot be cleanly separated from the paid Advanced tier. The existing Press billing covers hosting but not the AI subscription, and it does not integrate with Arabic payment gateways.

## Solution

Build a hybrid billing and subscription service. Billing combines the Press system with a custom service that handles AI subscription line items and usage. Subscriptions combine Press with a custom subscription manager that tracks state and renewal. Both integrate with Press over REST. Payments go through Arabic gateways (HyperPay and PayTabs), integrated by webhook so payment state updates are pushed and verified rather than polled. Subscription state is exposed to layer 03 so it can gate Advanced AI features.

## User Stories

1. As an AlbannaTech customer, I want a clear invoice each period, so that I know what I am paying for
2. As an AlbannaTech customer, I want to pay with an Arabic payment gateway, so that I can pay the way I am used to
3. As an AlbannaTech customer, I want to choose HyperPay or PayTabs, so that I can use my preferred gateway
4. As an AlbannaTech customer, I want the Basic AI agent for free with hosting, so that I pay nothing extra for everyday help
5. As an AlbannaTech customer, I want to subscribe to the Advanced Pro agent annually, so that I get premium capabilities
6. As an AlbannaTech customer, I want my subscription to renew automatically, so that service does not lapse
7. As an AlbannaTech customer, I want to be notified before renewal, so that I am not surprised
8. As an AlbannaTech customer, I want a failed payment retried, so that a temporary problem does not cut my service
9. As an AlbannaTech customer, I want my Advanced features to unlock immediately after payment, so that I can use what I paid for
10. As an AlbannaTech customer, I want my Advanced features to lock when payment fails past a grace period, so that billing is fair
11. As an AlbannaTech customer, I want to see my subscription status, so that I know where I stand
12. As an AlbannaTech operator, I want one place that holds subscription state, so that layer 03 can gate features against it
13. As an AlbannaTech operator, I want payment webhooks verified, so that forged notices cannot grant access
14. As an AlbannaTech operator, I want billing to sync with Press over REST, so that hosting and AI charges appear on one invoice
15. As an AlbannaTech operator, I want to reconcile gateway payments with our records, so that I can trust the numbers
16. As an AlbannaTech operator, I want to issue refunds, so that I can correct mistakes
17. As an AlbannaTech operator, I want usage-based line items, so that metered charges are billed correctly
18. As an AlbannaTech operator, I want subscription events recorded, so that I can audit the lifecycle
19. As an AlbannaTech operator, I want the billing service to be independent of the MCP servers, so that a billing outage does not stop operations
20. As an AlbannaTech operator, I want to switch a customer between Basic and Advanced, so that upgrades and downgrades are clean

## Implementation Decisions

### Billing service
- **Model**: hybrid — the Press system handles hosting lines; a custom billing service handles AI subscription lines and usage.
- **Integration with Press**: REST API for invoice creation and synchronization.
- **Line items**: hosting, Advanced Pro subscription, and metered usage where applicable.

### Subscription
- **Model**: hybrid — Press tracks its own subscriptions; a custom subscription manager tracks AI subscription state and renewal.
- **Integration with Press**: REST API to validate account standing and annual renewal state.
- **State**: exposed to layer 03 so it can gate Advanced AI features.
- **Lifecycle**: active, grace (payment failed, features still on), suspended (features off), cancelled.
- **Renewal**: annual for Advanced Pro; automatic with advance notification.

### Payment gateway
- **Gateways**: HyperPay and PayTabs.
- **Integration**: webhook for payment notifications (success, failure, refund). Webhooks are signature-verified before any state change.
- **Retries**: failed payments retried within the grace window.

### Tiering
- **Basic**: free with hosting.
- **Advanced Pro**: paid annual. Unlocks on payment; locks when payment fails past grace.

## Testing Decisions

### The seam
The seam is the **subscription lifecycle**: drive a subscription through its states (created → active → grace → suspended → cancelled) and assert the observable outcome (features unlocked or locked, invoices issued, notifications sent). Tests do not assert on internal table rows or gateway SDK calls; gateway interaction is simulated via a fake webhook.

### What makes a good test
- A test creates an Advanced subscription, simulates a successful payment webhook, and asserts Advanced features are unlocked.
- A test simulates a failed payment, advances past grace, and asserts Advanced features are locked.
- A test sends a webhook with an invalid signature and asserts no state change.
- A test asserts a renewal notification is produced before the renewal date.
- A test asserts a Basic subscription yields a free AI line and no charge.
- A test asserts Press receives a synchronized invoice over REST (against a fake Press endpoint).
- Tests do not assert on the internal representation of a subscription record.

### Which modules will be tested
- Subscription state machine: every transition and its gating effect
- Payment webhook handling: valid, invalid signature, duplicate
- Invoice generation and Press synchronization
- Retry and grace behavior
- Tier switching: Basic ↔ Advanced
- Refund handling

### Prior art
- The Press app already handles Stripe/Razorpay/PayPal webhooks; existing webhook tests show the pattern of posting a signed payload and asserting the resulting document state.
- Existing Press billing doctypes and their tests provide the model for invoice assertions.

## Out of Scope

- The MCP servers — layer 01.
- The AI agent — layer 02.
- Authentication and permission internals — layer 03 (this layer only provides subscription state for gating).
- Additional gateways beyond HyperPay and PayTabs (e.g. Stripe) in this phase.
- Tax computation and jurisdiction-specific compliance.
- Multi-currency beyond what the gateways natively support.

## Further Notes

- Billing is deliberately independent of the MCP servers: an outage here must not stop infrastructure operations.
- Webhooks are the source of truth for payment state; polling is avoided.
- Subscription state is a single source that layer 03 reads to gate Advanced features.
