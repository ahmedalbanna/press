# Copyright (c) 2024, Frappe and Contributors
# See license.txt

from unittest.mock import Mock, PropertyMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase
from telegram.error import RetryAfter, TimedOut

from press.press.doctype.telegram_message.telegram_message import (
	TelegramMessage,
	send_telegram_message,
)
from press.telegram_utils import Telegram


def quarantine_backlog() -> list[str]:
	"""Take the site's real Telegram backlog out of the way, reversibly.

	`TelegramMessage.get_one()` returns the oldest `Queued` message site-wide,
	not the oldest one belonging to the caller. On a site with a production
	backlog, every test would therefore assert against someone else's rows, and
	`send_telegram_message` would walk the entire backlog before reaching the
	row under test.

	Returns the names that were flagged so they can be put back. This cannot
	rely on the test transaction rolling back, because `TelegramMessage.send`
	calls `frappe.db.commit()` itself.
	"""
	queued = frappe.get_all("Telegram Message", filters={"status": "Queued"}, pluck="name")
	if queued:
		frappe.db.set_value(
			"Telegram Message", {"name": ("in", queued)}, "status", "Sent", update_modified=False
		)
		frappe.db.commit()
	return queued


def restore_backlog(queued: list[str]) -> None:
	"""Undo `quarantine_backlog`, putting the site's own messages back.

	Also removes the rows the tests created. `TelegramMessage.send` commits as
	it goes, so `frappe.db.rollback()` in `tearDown` cannot undo them and they
	would otherwise accumulate in the site on every run.
	"""
	frappe.db.delete("Telegram Message", {"message": "Test Message"})
	frappe.db.commit()
	if queued:
		frappe.db.set_value(
			"Telegram Message", {"name": ("in", queued)}, "status", "Queued", update_modified=False
		)
		frappe.db.commit()


# These tests drive the queue, not the bot. `Telegram.send` is mocked, but
# `Telegram.__init__` still resolves a token from the site, and "unconfigured"
# is a branch of its own. Pin it to True so a real token is the stated
# precondition instead of an accident of the site's settings. `new=` rather
# than `new_callable=` keeps the patcher from injecting an extra argument, so
# the existing test signatures stay valid.
@patch.object(Telegram, "configured", new=PropertyMock(return_value=True))
@patch.object(Telegram, "send")
class TestTelegramMessage(FrappeTestCase):
	def setUp(self):
		self._backlog = quarantine_backlog()

	def tearDown(self):
		frappe.db.rollback()
		restore_backlog(self._backlog)

	def test_enqueue_creates_telegram_message(self, mock_send: Mock):
		"""Test if enqueue method creates Telegram Message"""

		before = frappe.db.count("Telegram Message")
		TelegramMessage.enqueue(message="Test Message")
		after = frappe.db.count("Telegram Message")
		self.assertEqual(after, before + 1)

	def test_enqueue_creates_telegram_message_with_queued_status(self, mock_send: Mock):
		"""Test if enqueue method creates Telegram Message with Queued status"""
		message = TelegramMessage.enqueue(message="Test Message")
		self.assertEqual(message.status, "Queued")

	def test_send_calls_telegram_send(self, mock_send: Mock):
		"""Test if send method calls Telegram send method"""
		TelegramMessage.enqueue(message="Test Message")
		send_telegram_message()
		mock_send.assert_called_once()

	def test_successful_send_call_sets_sent_status(self, mock_send: Mock):
		"""Test if successful send call sets status to Sent"""
		first = TelegramMessage.enqueue(message="Test Message")
		send_telegram_message()
		first.reload()
		self.assertEqual(first.status, "Sent")

	def test_failed_send_call_sets_error_status(self, mock_send: Mock):
		"""Test if failed send call sets status to Error"""
		mock_send.side_effect = Exception()
		first = TelegramMessage.enqueue(message="Test Message")
		self.assertRaises(Exception, TelegramMessage.send_one)
		first.reload()
		self.assertEqual(first.status, "Error")
		self.assertIn("Exception", first.error)

	def test_sends_messages_in_priority_order(self, mock_send: Mock):
		"""Test if messages are sent in priority order"""
		high = TelegramMessage.enqueue(message="Test Message", priority="High")
		medium = TelegramMessage.enqueue(message="Test Message", priority="Medium")
		low = TelegramMessage.enqueue(message="Test Message", priority="Low")

		self.assertEqual(TelegramMessage.get_one(), high)
		send_telegram_message()
		self.assertEqual(TelegramMessage.get_one(), medium)
		send_telegram_message()
		self.assertEqual(TelegramMessage.get_one(), low)
		send_telegram_message()

		low = TelegramMessage.enqueue(message="Test Message", priority="Low")
		medium = TelegramMessage.enqueue(message="Test Message", priority="Medium")
		high = TelegramMessage.enqueue(message="Test Message", priority="High")

		self.assertEqual(TelegramMessage.get_one(), high)
		send_telegram_message()
		self.assertEqual(TelegramMessage.get_one(), medium)
		send_telegram_message()
		self.assertEqual(TelegramMessage.get_one(), low)
		send_telegram_message()

	def test_sends_messages_in_creation_order(self, mock_send: Mock):
		"""Test if messages are sent in creation order"""
		first = TelegramMessage.enqueue(message="Test Message")
		second = TelegramMessage.enqueue(message="Test Message")

		self.assertEqual(TelegramMessage.get_one(), first)
		send_telegram_message()
		self.assertEqual(TelegramMessage.get_one(), second)
		send_telegram_message()

	def test_failed_send_network_error_increases_retry(self, mock_send: Mock):
		"""Test if failed send call because of network issues increases retry count"""
		mock_send.side_effect = TimedOut()
		first = TelegramMessage.enqueue(message="Test Message")
		self.assertRaises(TimedOut, TelegramMessage.send_one)
		first.reload()
		self.assertEqual(first.status, "Queued")
		self.assertEqual(first.retry_count, 1)

	def test_test_failed_send_after_max_retries_sets_error_status(self, mock_send: Mock):
		"""Test if failed send call after max_errors sets status to Error"""
		mock_send.side_effect = TimedOut()
		first = TelegramMessage.enqueue(message="Test Message")
		first.retry_count = 4
		first.save()
		self.assertRaises(TimedOut, TelegramMessage.send_one)
		first.reload()
		self.assertEqual(first.status, "Error")

	def test_failed_send_retry_after_doesnt_change_anything(self, mock_send: Mock):
		"""Test if failed send call because of rate limits doesn't change status"""
		mock_send.side_effect = RetryAfter(10)
		first = TelegramMessage.enqueue(message="Test Message")
		self.assertRaises(RetryAfter, TelegramMessage.send_one)
		first.reload()
		self.assertEqual(first.status, "Queued")

	def test_send_message_returns_on_empty_queue(self, mock_send: Mock):
		"""Test if send_telegram_message returns on empty queue"""
		first = TelegramMessage.enqueue(message="Test Message")
		first.status = "Sent"
		first.save()
		send_telegram_message()
		mock_send.assert_not_called()

	def test_send_message_does_not_raise_on_failure(self, mock_send: Mock):
		"""Test if send_telegram_message does not raise on failure"""
		mock_send.side_effect = Exception()
		first = TelegramMessage.enqueue(message="Test Message")
		send_telegram_message()
		first.reload()
		self.assertEqual(first.status, "Error")
		self.assertIn("Exception", first.error)


class TestTelegramMessageUnconfigured(FrappeTestCase):
	"""Telegram is off on this bench.

	No token exists on any Telegram Group or in Press Settings, so nothing here
	may reach the Bot API. `telegram.Bot` raises `InvalidToken` for a missing
	token, which is indistinguishable from a real delivery failure unless the
	unconfigured case is handled explicitly.
	"""

	def setUp(self):
		self._backlog = quarantine_backlog()

	def tearDown(self):
		frappe.db.rollback()
		restore_backlog(self._backlog)

	def test_backlog_drains_instead_of_stalling(self):
		"""A backlog left by an unconfigured deployment must not stall.

		`send_telegram_message` sends one message per invocation and returns, so
		draining is a matter of leaving `Queued`. Left `Queued` forever the
		backlog would never clear and the sender would walk past it on every
		tick instead.
		"""
		for _ in range(3):
			TelegramMessage.enqueue(message="Test Message")

		# One message per invocation is the sender's design, bounded by the
		# job timeout, so drive it as many times as there are messages.
		for _ in range(3):
			send_telegram_message()

		self.assertEqual(TelegramMessage.get_one(), None)
		self.assertEqual(
			frappe.db.count("Telegram Message", {"status": "Queued", "message": "Test Message"}), 0
		)

	def test_status_is_error_with_the_actual_reason(self):
		first = TelegramMessage.enqueue(message="Test Message")

		send_telegram_message()

		first.reload()
		self.assertEqual(first.status, "Error")
		self.assertIn("not configured", first.error)
		self.assertNotIn("InvalidToken", first.error)

	def test_sender_does_not_raise(self):
		"""An unconfigured deployment is not an exception; it is a state."""
		TelegramMessage.enqueue(message="Test Message")
		send_telegram_message()
