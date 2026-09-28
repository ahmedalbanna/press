# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import time

from frappe.tests.utils import FrappeTestCase

from press.utils.clock import cache, now_utc


class TestCache(FrappeTestCase):
	"""The TTL cache in `press.utils.clock`.

	Its expiry bookkeeping used `datetime.utcnow()`, which is removed in Python
	3.15. Both sides of the comparison were naive, so switching to aware UTC is
	behaviour-preserving.
	"""

	def test_now_utc_is_timezone_aware_utc(self):
		self.assertIsNotNone(now_utc().tzinfo)
		self.assertEqual(now_utc().utcoffset().total_seconds(), 0)

	def test_result_is_cached_within_the_ttl(self):
		calls = []

		@cache(seconds=60)
		def counted():
			calls.append(1)
			return len(calls)

		self.assertEqual(counted(), 1)
		self.assertEqual(counted(), 1)
		self.assertEqual(len(calls), 1)

	def test_cache_clears_once_the_ttl_passes(self):
		calls = []

		@cache(seconds=1)
		def counted():
			calls.append(1)
			return len(calls)

		self.assertEqual(counted(), 1)
		time.sleep(1.1)
		self.assertEqual(counted(), 2)
		self.assertEqual(len(calls), 2)

	def test_expiration_is_aware(self):
		"""Naive and aware cannot be compared, so this must not drift back."""

		@cache(seconds=60)
		def noop():
			return 1

		self.assertIsNotNone(noop.expiration.tzinfo)
		# The wrapper compares `now_utc()` against `expiration`. A naive value on
		# either side raises TypeError here, so a call is the assertion.
		self.assertEqual(noop(), 1)
