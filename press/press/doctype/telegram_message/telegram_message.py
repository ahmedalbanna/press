# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import traceback

import frappe
from frappe.model.document import Document
from frappe.query_builder import Case, Interval
from frappe.query_builder.functions import Now
from telegram.error import NetworkError, RetryAfter

from press.telegram_utils import Telegram


class TelegramMessage(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		error: DF.Code | None
		group: DF.Data | None
		message: DF.Code
		priority: DF.Literal["High", "Medium", "Low"]
		retry_count: DF.Int
		status: DF.Literal["Queued", "Sent", "Error"]
		topic: DF.Data | None
	# end: auto-generated types

	def send(self):
		try:
			telegram = Telegram(self.topic, self.group)
			if not telegram.configured:
				# No bot token on the group or in Press Settings. `telegram.Bot`
				# raises InvalidToken for a missing token, which reads like a
				# delivery failure and walks straight into the "don't retry"
				# branch. Nothing will change on a retry either, so record the
				# actual reason. Leaving it Queued is worse: the sender would
				# walk the whole backlog on every tick and never drain it.
				self.status = "Error"
				self.error = (
					"Telegram is not configured: set a bot token on the Telegram Group or in Press Settings"
				)
			else:
				if not self.group:
					self.group = telegram.group
				if not self.topic:
					self.topic = telegram.topic
				telegram.send(self.message, reraise=True)
				self.status = "Sent"
		except RetryAfter:
			# Raise an exception that will be caught by the scheduler
			# Try again after some time
			raise
		except NetworkError:
			# Try again. Not more than 5 times
			self.retry_count += 1
			self.error = traceback.format_exc()
			if self.retry_count >= 5:
				self.status = "Error"
			raise
		except Exception:
			# It's unlikely that this error will be resolved by retrying
			# Fail immediately
			self.error = traceback.format_exc()
			self.status = "Error"
			raise
		finally:
			self.save()
			frappe.db.commit()

	@staticmethod
	def enqueue(
		message: str,
		topic: str | None = None,
		group: str | None = None,
		priority: str = "Medium",
	):
		"""Enqueue message for sending"""
		return frappe.get_doc(
			{
				"doctype": "Telegram Message",
				"message": message,
				"priority": priority,
				"topic": topic,
				"group": group,
			}
		).insert(ignore_permissions=True)

	@staticmethod
	def get_one() -> "TelegramMessage | None":
		# Frappe 16 validates `order_by` and accepts only plain field names, so
		# the MariaDB FIELD() trick this used to rely on now raises
		# `Invalid field format in Order By: FIELD(priority`. A `Case` expresses
		# the same High -> Medium -> Low ranking, and the query builder is not
		# subject to that check.
		table = frappe.qb.DocType("Telegram Message")
		priority = (
			Case().when(table.priority == "High", 0).when(table.priority == "Medium", 1).else_(2)  # Low
		)
		first = (
			frappe.qb.from_(table)
			.select(table.name)
			.where(table.status == "Queued")
			.orderby(priority, table.creation)
			.limit(1)
			.run()
		)
		if first:
			return frappe.get_doc("Telegram Message", first[0][0])
		return None

	@staticmethod
	def send_one() -> None:
		message = TelegramMessage.get_one()
		if message:
			return message.send()
		return None

	@staticmethod
	def clear_old_logs(days=30):
		table = frappe.qb.DocType("Telegram Message")
		frappe.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
		frappe.db.commit()


def send_telegram_message():
	"""Send one queued telegram message"""
	from press.utils.jobs import has_job_timeout_exceeded

	# Go through the queue till either of these things happen
	# 1. There are no more queued messages
	# 2. We successfully send a message
	# 3. Telegram asks us to stop (RetryAfter)
	# 4. We encounter an error that is not recoverable by retrying
	# (attempt 5 retries and remove the message from queue)
	while message := TelegramMessage.get_one():
		if has_job_timeout_exceeded():
			return
		try:
			message.send()
			return
		except RetryAfter:
			# Retry in the next invocation
			return
		except Exception:
			# Try next message
			pass
