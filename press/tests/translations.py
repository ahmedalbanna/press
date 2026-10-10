"""Strings an Arabic interface reads better untranslated.

Kept in one place because the list is knowledge, not data: product names,
architecture identifiers, and operators that are not prose. Test modules assert
against it, and two copies of the same allowlist is exactly the drift the
translation suite exists to catch -- the second one to be edited never learns
about the first.

Every vendor below is written into the catalog with an RLM mark (U+200F) ahead of
it, so a Latin word inside an Arabic sentence still lays out left to right. That
is why the rule checks for Arabic script rather than for a changed value.

A string added here must be a deliberate call a reviewer can repeat, not "we
could not translate it". test_translation_catalog fails if any entry's Arabic
silently equals its English outside this set.
"""

# Operators and markup names, not prose.
NON_PROSE = frozenset({"!=", "==", "HTML", "Markdown"})

# Our own product name, which is "Press" everywhere the customer sees it.
PRODUCT_NAME = frozenset({"Press"})

# Markup that carries no words. The divs are DOM hooks for a chart and the span
# wraps the brand name, so there is nothing to translate in any of them.
MARKUP = frozenset(
	{
		'<div id="problematic_sites_report"></div>',
		'<div id="server_downtime_report"></div>',
		'<div id="site_downtime_report"></div>',
		'<span class="h4">AlbannaTech</span>',
	}
)

# Protocol, architecture and platform identifiers. An Arabic operator reads these
# in Latin: a transliteration of "innodb" helps nobody.
IDENTIFIERS = frozenset(
	{
		"amd64",
		"API Key",
		"API Secret",
		"arm64",
		"CNAME",
		"DNS",
		"ext4",
		"Frappe Partner",
		"gp2",
		"gp3",
		"innodb",
		"IPv6",
		"jemalloc",
		"JSON",
		"nfs",
		# `Saas` is a second source spelling of `SaaS` that exists in the app; it
		# stays Latin like its twin rather than being silently corrected, because
		# the catalog test compares the two character for character.
		"Saas",
		"SaaS",
		"SSH",
		"SSH Proxy",
		"TCMalloc",
		"TCP",
		"UDP",
		"UUID",
		"Webhook",
		"x86_64",
	}
)

# Third-party product and vendor names, which no white-label renames.
VENDOR_NAMES = frozenset(
	{
		"AWS",
		"AWS - RDS",
		"AWS EC2",
		"AWS RDS",
		"AWS Route 53",
		"AWS S3",
		"Digital Ocean",
		"DigitalOcean",
		"Docker",
		"ERPNext",
		"Frappe Cloud",
		"Frappe Compute",
		"Grafana",
		"Google Search Console",
		"Hetzner",
		"Kibana",
		"Let's Encrypt",
		"Mailgun",
		"MariaDB",
		"Nginx",
		"OCI",
		"PayPal",
		"Plausible",
		"ProxySQL",
		"Raven",
		"Scaleway",
		"Sentry",
		"Spamd",
		"Telegram",
		"Twilio",
		"Vodacom",
		"VPN",
		"WhatsApp",
		"Wireguard",
	}
)

UNTRANSLATED_BY_CHOICE = NON_PROSE | PRODUCT_NAME | MARKUP | IDENTIFIERS | VENDOR_NAMES

# Source strings that quote Arabic on purpose. The column-shift check exists to
# catch Arabic landing in the English column, so a source that contains Arabic by
# design has to be named rather than failing the check.
ARABIC_IN_SOURCE = frozenset(
	{
		# Help text for Press Language.language_name: it asks for how speakers of
		# the language call it themselves and gives العربية as the example.
		"How speakers of the language call it themselves, e.g. العربية for Arabic.",
	}
)
