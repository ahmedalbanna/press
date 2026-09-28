# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt
"""Clock helpers: reading the current time, and caching against it.

Named `clock` rather than `time` on purpose. Importing a submodule binds it as an
attribute on the parent package, so `press/utils/time.py` would overwrite the
stdlib `time` that `press.utils` itself imports -- which only shows up at runtime,
in a different module, as `module 'press.utils.time' has no attribute 'time'`.

`now_utc` is deliberately not called `now`: `frappe.utils.now()` returns a
*string*, and the two are easy to confuse at a call site.
"""

import functools
from datetime import datetime, timedelta, timezone


def now_utc() -> datetime:
	"""Current time as an aware UTC datetime.

	Stands in for `datetime.utcnow()`, which is removed in Python 3.15. Use it
	whenever a datetime is compared against another one: mixing a naive value
	with an aware one raises `TypeError` at the comparison, not at construction.
	"""
	return datetime.now(timezone.utc)


def cache(seconds: int, maxsize: int = 128, typed: bool = False):
	"""Memoize a function's result for `seconds`, keyed on its arguments.

	In-process, so it needs neither a site nor redis, unlike
	`frappe.utils.caching.redis_cache`.
	"""

	def wrapper_cache(func):
		func = functools.lru_cache(maxsize=maxsize, typed=typed)(func)
		func.delta = timedelta(seconds=seconds)
		func.expiration = now_utc() + func.delta

		@functools.wraps(func)
		def wrapped_func(*args, **kwargs):
			if now_utc() >= func.expiration:
				func.cache_clear()
				func.expiration = now_utc() + func.delta

			return func(*args, **kwargs)

		return wrapped_func

	return wrapper_cache
