# 01: Foundation — Brand Assets & CSS Variables

**What to build:** Copy AlbannaTech logo and favicon to public directories, update hooks.py app metadata, define CSS custom properties for brand colors and fonts, and add Google Fonts links. This is the foundation that all other rebranding tickets depend on.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Copy AlbannaTech SVG logo to `press/public/images/albannatech-logo.svg`
- [ ] Copy AlbannaTech favicon to `press/public/images/favicon.svg` and `dashboard/public/favicon.png`
- [ ] Update `hooks.py`: app_title="AlbannaTech", app_publisher="AlbannaTech", app_description="Managed ERPNext Hosting", app_email="support@albannatech.com", app_color="#0EA5E9"
- [ ] Define CSS custom properties in `saas-next.css`: --primary: #0F172A, --secondary: #0EA5E9, --accent: #10B981, --bg-light: #F8FAFC, --bg-dark: #020617
- [ ] Define CSS custom properties in `marketplace-next.css` with same color system
- [ ] Add Google Fonts links (Cairo/Tajawal for Arabic, Inter/Plus Jakarta Sans for English) to dashboard/index.html
- [ ] Verify logo files render correctly in browser
- [ ] Verify hooks.py metadata appears in Press desk
