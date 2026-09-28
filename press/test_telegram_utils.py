# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

from unittest.mock import AsyncMock, PropertyMock, patch

import telegram
import frappe
from frappe.tests.utils import FrappeTestCase
from telegram.constants import MessageLimit, ParseMode

from press.telegram_utils import Telegram


class TestTelegram(FrappeTestCase):
	"""Covers the python-telegram-bot v20+ async migration in `telegram_utils`.

	The bot API is never contacted: `Bot.initialize` and `Bot.send_message` are
	replaced with async mocks, so these assert on how `Telegram` drives the
	coroutine (truncation, parse mode, topic routing, error handling) rather than
	on the network.
	"""

	def _client(self, **attrs):
		# `Telegram.__init__` reads three different shapes, so the stub has to
		# answer per doctype: a dict-like for Press Settings, a tuple for
		# Telegram Group, and a scalar for the topic.
		def get_value(doctype, name=None, fields=None, **kwargs):
			if doctype == "Press Settings":
				return frappe._dict({"telegram_bot_token": "token", "telegram_alerts_chat_group": "Errors"})
			if doctype == "Telegram Group":
				return ("token", "123")
			return 42

		with patch("frappe.db.get_value", side_effect=get_value):
			client = Telegram()

		client.token = "token"
		client.chat_id = "123"
		client.topic_id = 42
		for key, value in attrs.items():
			setattr(client, key, value)
		return client

	def test_send_passes_text_parse_mode_and_topic(self):
		client = self._client()

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "send_message", new=AsyncMock(return_value="sent")) as send:
				self.assertEqual(client.send("hello", html=True), "sent")

		kwargs = send.await_args.kwargs
		self.assertEqual(kwargs["chat_id"], "123")
		self.assertEqual(kwargs["text"], "hello")
		self.assertEqual(kwargs["parse_mode"], ParseMode.HTML)
		self.assertEqual(kwargs["message_thread_id"], 42)

	def test_send_defaults_to_markdown(self):
		client = self._client()

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "send_message", new=AsyncMock(return_value="sent")) as send:
				client.send("plain")

		self.assertEqual(send.await_args.kwargs["parse_mode"], ParseMode.MARKDOWN)

	def test_send_truncates_oversized_message(self):
		client = self._client()
		oversized = "x" * (MessageLimit.MAX_TEXT_LENGTH + 100)

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "send_message", new=AsyncMock(return_value="sent")) as send:
				client.send(oversized)

		self.assertEqual(len(send.await_args.kwargs["text"]), MessageLimit.MAX_TEXT_LENGTH)

	def test_send_is_a_noop_without_a_message(self):
		client = self._client()

		with patch.object(telegram.Bot, "send_message", new=AsyncMock()) as send:
			self.assertIsNone(client.send(""))
			self.assertIsNone(client.send(None))

		send.assert_not_awaited()

	def test_send_swallows_errors(self):
		client = self._client()
		boom = AsyncMock(side_effect=telegram.error.NetworkError("down"))

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "send_message", new=boom):
				with patch("press.telegram_utils.log_error") as log_error:
					self.assertIsNone(client.send("hello"))

		log_error.assert_called_once()

	def test_send_reraises_when_asked(self):
		client = self._client()
		boom = AsyncMock(side_effect=telegram.error.NetworkError("down"))

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "send_message", new=boom):
				with self.assertRaises(telegram.error.NetworkError):
					client.send("hello", reraise=True)

	def test_get_username_initializes_the_bot(self):
		client = self._client()

		with patch.object(telegram.Bot, "initialize", new=AsyncMock()):
			with patch.object(telegram.Bot, "username", new_callable=PropertyMock, return_value="mybot"):
				self.assertEqual(client.get_username(), "mybot")


class TestTelegramUnconfigured(FrappeTestCase):
	"""Telegram is off on this bench: there is no bot token to send with.

	`telegram.Bot` raises `InvalidToken` for a missing token before it opens a
	connection, so without this branch every alert would raise and write an
	Error Log blaming the network.
	"""

	def _unconfigured(self):
		# No Telegram Group row and no token in Press Settings, which is the
		# state of press.localhost.
		def get_value(doctype, name=None, fields=None, **kwargs):
			if doctype == "Press Settings":
				return frappe._dict({"telegram_bot_token": None, "telegram_alerts_chat_group": ""})
			return None

		with patch("frappe.db.get_value", side_effect=get_value):
			return Telegram()

	def test_configured_is_false_without_a_token(self):
		self.assertFalse(self._unconfigured().configured)

	def test_send_is_a_silent_noop(self):
		"""No token is a deployment choice, not an incident: log nothing."""
		client = self._unconfigured()

		with patch.object(telegram.Bot, "send_message", new=AsyncMock()) as send:
			with patch("press.telegram_utils.log_error") as log_error:
				self.assertIsNone(client.send("hello"))

		send.assert_not_awaited()
		log_error.assert_not_called()

	def test_send_is_a_noop_even_when_reraise_is_asked(self):
		"""`reraise` must not turn "off" into an exception."""
		client = self._unconfigured()

		self.assertIsNone(client.send("hello", reraise=True))

	def test_get_username_is_none(self):
		self.assertIsNone(self._unconfigured().get_username())

	def test_respond_ignores_anything_without_a_handle(self):
		"""With no @handle to match, the webhook must not answer a message."""
		client = self._unconfigured()
		client.respond(
			{"chat": {"id": 1}, "text": "ping", "entities": [{"type": "mention", "offset": 0, "length": 4}]}
		)
