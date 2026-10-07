# AlbannaTech White-Label Rebranding — Spec

## Problem Statement

AlbannaTech is a technology and software company that provides managed cloud hosting, ERPNext/Frappe customization, data seeding, AI agents, and flexible deployment options. They have forked the Frappe Press platform to power their hosting business, but the platform currently carries Frappe Cloud's branding throughout — in the dashboard, signup/login pages, email templates, marketplace, and public pages. AlbannaTech needs the platform to present their own brand identity so that customers perceive it as an AlbannaTech product, not a Frappe Cloud instance.

## Solution

Rebrand the Press platform across all customer-facing surfaces to AlbannaTech's visual identity. This covers the dashboard (the primary customer interface), signup/login pages (first touchpoint for new customers), email templates (direct communication channel), and the marketplace (app discovery). The rebranding includes: AlbannaTech's logo and favicon, their color palette (deep navy `#0F172A`, cyan `#0EA5E9`, emerald `#10B981`), bilingual support (Arabic + English with RTL/LTR), and AlbannaTech's domain and contact information in all relevant places.

## User Stories

1. As an AlbannaTech customer, I want to see the AlbannaTech logo in the dashboard header, so that I feel I am using AlbannaTech's platform
2. As an AlbannaTech customer, I want the dashboard to use AlbannaTech's color scheme (navy/cyan/emerald), so that the interface feels familiar and professional
3. As an AlbannaTech customer, I want to switch between Arabic and English in the dashboard, so that I can work in my preferred language
4. As an AlbannaTech customer, I want the dashboard to support RTL layout when Arabic is selected, so that the interface reads naturally
5. As a new customer, I want to see AlbannaTech's branding on the signup page, so that I trust I am creating an account with AlbannaTech
6. As a new customer, I want the login page to show AlbannaTech's logo and colors, so that I feel secure entering my credentials
7. As an AlbannaTech customer, I want email notifications to carry AlbannaTech's branding, so that I recognize them as legitimate communications
8. As an AlbannaTech customer, I want email templates to be sent in my preferred language (Arabic or English), so that I can read them comfortably
9. As an AlbannaTech customer, I want the marketplace navbar to show AlbannaTech's logo, so that I feel I am browsing AlbannaTech's app store
10. As an AlbannaTech customer, I want the marketplace footer to link to AlbannaTech's resources, so that I can find support and documentation
11. As an AlbannaTech customer, I want the favicon to show AlbannaTech's icon, so that I can identify the platform in my browser tabs
12. As an AlbannaTech customer, I want the browser tab title to say "AlbannaTech" instead of "Frappe Cloud", so that I can identify the platform
13. As an AlbannaTech team member, I want the Press desk to show AlbannaTech's app title and publisher, so that the internal tool feels like our own
14. As an AlbannaTech team member, I want the app icon and color in the desk to match our brand, so that the internal experience is consistent
15. As a new customer, I want the signup page to reference AlbannaTech's Terms of Service and Privacy Policy, so that I know which legal entity I am engaging with
16. As an AlbannaTech customer, I want support links to point to AlbannaTech's support channels, so that I can get help from the right team
17. As an AlbannaTech customer, I want the dark mode to use AlbannaTech's dark background color (#020617), so that the dark experience feels on-brand
18. As an AlbannaTech customer, I want the light mode to use AlbannaTech's light background color (#F8FAFC), so that the light experience feels clean and professional
19. As an AlbannaTech customer, I want the Arabic font (Cairo/Tajawal) to be applied throughout the Arabic interface, so that text is clear and readable
20. As an AlbannaTech customer, I want the English font (Inter/Plus Jakarta Sans) to be applied throughout the English interface, so that text is professional and legible

## Implementation Decisions

### Brand Assets
- **Logo**: SVG wordmark with icon mark (A+T fusion in a rounded square), "AlbannaTech" text with "Tech" in cyan, and Arabic subtitle "البناء للتكنولوجيا" — provided as SVG files
- **Favicon**: 64x64 SVG with the A+T icon mark on navy background with cyan accent
- **Logo placement**: Dashboard header, signup page, login page, marketplace navbar, marketplace footer, email header

### Color System
- **Primary**: `#0F172A` (deep navy) — headers, primary text, dark backgrounds
- **Secondary**: `#0EA5E9` (cyan/sky blue) — accents, links, highlights, "Tech" in logo
- **Accent**: `#10B981` (emerald green) — success states, active server status, positive indicators
- **Light background**: `#F8FAFC` — light mode base
- **Dark background**: `#020617` — dark mode base
- **Neutrals**: Slate scale for borders, secondary text, muted elements

### Typography
- **Arabic**: Cairo or Tajawal — loaded from Google Fonts
- **English**: Inter or Plus Jakarta Sans — loaded from Google Fonts
- **Font stack**: System font fallbacks for offline resilience

### Bilingual Support
- Full Arabic + English translation for dashboard, signup, login, and email templates
- RTL layout support when Arabic is active
- Language preference stored per user
- Email templates sent in the recipient's preferred language

### Domain & Contact
- Temporary domain for development (localhost or press.local)
- Production domain (albannatech.com or erp.albannatech.com) configured at launch
- Support email: support@albannatech.com (or as specified by AlbannaTech)
- All frappecloud.com references replaced with AlbannaTech equivalents

### Priority Order
1. **Phase 1A — Dashboard**: Title, favicon, logo, colors, fonts, bilingual
2. **Phase 1B — Signup/Login**: Logo, colors, branding, legal links, bilingual
3. **Phase 1C — Email Templates**: Base template branding, logo, colors, bilingual
4. **Phase 1D — Marketplace**: Navbar logo, footer links, logo, colors
5. **Phase 1E — Public Pages**: Deferred or minimal customization

### Technical Approach
- **hooks.py**: Update app_title, app_publisher, app_description, app_email, app_color, app_icon
- **Dashboard index.html**: Update title, add favicon link, add Google Fonts links
- **CSS**: Update CSS custom properties (variables) in saas-next.css and marketplace-next.css
- **Templates**: Replace hardcoded Frappe Cloud references with AlbannaTech equivalents
- **Press Settings**: Update default domain, support email, and other configurable fields
- **Static Assets**: Copy SVG logo and favicon to appropriate public directories

## Testing Decisions

### What makes a good test
- Tests verify external behavior: what the user sees (rendered HTML, computed styles, visible text)
- Tests do not verify implementation details: specific CSS class names, internal DOM structure, JavaScript function names
- Tests check that branding elements are present and correct (logo image, brand colors, company name)
- Tests verify bilingual content renders correctly in both languages

### Which modules will be tested
- **Template rendering**: Verify that SaaS signup, login, and marketplace templates render with AlbannaTech branding
- **CSS variables**: Verify that brand colors are correctly defined as CSS custom properties
- **Email templates**: Verify that the email base template includes AlbannaTech logo and branding
- **Dashboard HTML**: Verify that the dashboard entry point includes correct title, favicon, and font links
- **Hooks configuration**: Verify that app metadata fields contain AlbannaTech values

### Prior art
- The Press app has existing tests in `press/tests/` for doctype logic
- UI tests exist in `dashboard/tests-e2e/` using Playwright
- Template tests can follow the pattern of existing Python tests that render templates and assert on output

## Out of Scope

- **Functional customizations**: AI agents integration, data seeding workflows, custom ERPNext workflows, MCP integrations — these are Phase 2
- **Landing page**: Custom marketing/landing page for AlbannaTech — deferred
- **Documentation pages**: Frappe docs customization — deferred or minimal
- **DNS/SSL setup**: Production domain configuration — done at launch time
- **Payment gateway configuration**: Stripe/Razorpay/PayPal setup for AlbannaTech — separate task
- **Email delivery setup**: SMTP configuration for sending AlbannaTech-branded emails — separate task
- **Logo design**: Final logo design — using provided SVG wordmark as placeholder
- **Translation completeness**: Full Arabic translation of all dashboard strings — may be incremental

## Further Notes

- The provided SVG logo files are temporary placeholders until a final brand logo is produced
- The color palette and typography choices reflect AlbannaTech's brand guidelines as specified by the company
- All frappecloud.com, frappe.io, and erpnext.com references in customer-facing surfaces should be replaced with AlbannaTech equivalents
- The rebranding should be done in a way that makes future updates from upstream frappe/press manageable — avoid deep forks where possible, prefer overrides and template customizations
- Dark mode support should be implemented using CSS custom properties so that both light and dark themes use AlbannaTech's color palette
- The bilingual approach should use Frappe's built-in translation infrastructure where possible, with custom translations for AlbannaTech-specific strings
