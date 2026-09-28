# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt


import asyncio

import frappe
import telegram
from telegram.constants import MessageLimit, ParseMode
from telegram.request import HTTPXRequest

from press.utils import log_error

# Network calls are short and one-shot: alerts are sent from request handlers and
# background jobs, neither of which run inside an event loop.
REQUEST_TIMEOUT = 3.0


class _Call:
	"""A token plus the coroutine body to run against a freshly opened bot."""

	__slots__ = ("token", "run")

	def __init__(self, token, run):
		self.token = token
		self.run = run


def _run(coro):
	"""Run one Telegram coroutine on a throwaway event loop.

	The bot is opened *inside* the loop and closed with it, because the HTTPX
	connection pool is bound to the loop that created it. Reusing a bot across
	`asyncio.run` calls leaks connections and eventually fails.
	"""

	async def runner():
		async with telegram.Bot(
			token=coro.token,
			request=HTTPXRequest(connect_timeout=REQUEST_TIMEOUT, read_timeout=REQUEST_TIMEOUT),
		) as bot:
			return await coro.run(bot)

	return asyncio.run(runner())


class Telegram:
	def __init__(self, topic: str | None = None, group: str | None = None):
		settings = frappe.db.get_value(
			"Press Settings",
			None,
			["telegram_bot_token", "telegram_alerts_chat_group"],
			as_dict=True,
		)
		self.group = group or settings.telegram_alerts_chat_group
		telegram_group = frappe.db.get_value("Telegram Group", self.group, ["token", "chat_id"])
		token, chat_id = telegram_group if telegram_group else (None, None)
		self.token = token or settings.telegram_bot_token
		self.chat_id = chat_id
		self.topic = topic
		self.topic_id = frappe.db.get_value(
			"Telegram Group Topic", {"parent": self.group, "topic": topic}, "topic_id"
		)

	@property
	def configured(self) -> bool:
		"""Whether there is a bot token to send with.

		`telegram.Bot` rejects a missing token before it opens a connection, so an
		unconfigured deployment cannot send at all. Callers need to tell that apart
		from a send that was attempted and failed: one is a deployment choice, the
		other is an incident worth an Error Log.
		"""

		return bool(self.token)

	def send(self, message, html=False, reraise=False):
		if not message or not self.configured:
			return None
		try:
			text = message[: MessageLimit.MAX_TEXT_LENGTH]
			parse_mode = self._get_parse_mode(html)

			async def run(bot):
				return await bot.send_message(
					chat_id=self.chat_id,
					text=text,
					parse_mode=parse_mode,
					message_thread_id=self.topic_id,
				)

			return _run(_Call(self.token, run))
		except Exception:
			if reraise:
				raise
			log_error(
				"Telegram Bot Error",
				message=message,
				html=html,
				chat_id=self.chat_id,
				topic_id=self.topic_id,
			)

	def _get_parse_mode(self, html):
		if html:
			return ParseMode.HTML
		return ParseMode.MARKDOWN

	def get_username(self):
		"""The bot's own @handle.

		`Bot.username` is only populated after `initialize()`, which is async in
		v20+ (it used to be a plain cached attribute in v13).

		Returns None when unconfigured, which makes the `@handle` comparison in
		`respond` match nothing and the webhook a no-op.
		"""

		if not self.configured:
			return None

		async def run(bot):
			await bot.initialize()
			return bot.username

		return _run(_Call(self.token, run))

	def respond(self, message):
		if not message:
			return

		# Only respond to message from the Telegram alerts group
		if self.chat_id != str(message["chat"]["id"]):
			return

		# Respond on the same topic
		self.topic_id = message.get("message_thread_id")

		text = message["text"]
		entities = message.get("entities", [])
		# Ignore pointless chatter
		if not entities or entities[0]["type"] != "mention":
			return

		entity = entities[0]
		begin = entity["offset"]
		end = entity["offset"] + entity["length"]

		mention = text[begin:end]
		# Only respond to messages mentioning the bot
		if mention != f"@{self.get_username()}":
			return

		command = text.replace(mention, "")
		response = self.process(command.strip())
		if response:
			self.send(response)

	def process(self, command):
		arguments = command.split(" ")

		if len(arguments) == 1:
			commands = {
				"help": show_help_message,
				"ping": frappe.ping,
			}
			return commands.get(arguments[0], what)(*arguments[1:])
		if len(arguments) == 4:
			doctype, name, action, key = arguments
			commands = {"get": get_value, "execute": execute}
			return commands.get(action, what)(frappe.unscrub(doctype), name, key)
		if len(arguments) >= 5:
			doctype, name, action, key, *values = arguments
			commands = {
				"set": set_value,
				"execute": execute,
			}
			if action == "set" and len(values) == 1:
				return commands.get(action, what)(frappe.unscrub(doctype), name, key, values[0])
			return commands.get(action, what)(frappe.unscrub(doctype), name, key, *values)
		return what()


def set_value(doctype, name, field, value, *args):
	try:
		document = frappe.get_doc(doctype, name)
		document.set(field, value)
		document.save()
	except Exception:
		return f"```{frappe.get_traceback()}```"


def get_value(doctype, name, field, *args):
	try:
		return frappe.db.get_value(doctype, name, field)
	except Exception:
		return f"```{frappe.get_traceback()}```"


def execute(doctype, name, method, *args):
	# return "EXECUTE", doctype, name, method
	try:
		document = frappe.get_doc(doctype, name)
		return document.run_method(method, *args)
	except Exception:
		return f"```{frappe.get_traceback()}```"


def show_help_message(*args):
	return HELP_MESSAGE


def what(*args):
	return "What are you talking about?"


HELP_MESSAGE = """Try one of these

doctype name execute method
doctype name get field
doctype name set field value
doctype name execute method argument1 argument2 ...

doctype = site|bench|server|proxy-server|database-server

```
server f17.frappe.cloud execute reboot```
```
site docs.frappe.cloud get status```
```
bench docs.frappe.cloud set auto_scale_workers 0```
```
server f17.frappe.cloud execute increase_disk_size 25```
"""
