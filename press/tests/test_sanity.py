from unittest.mock import patch

import frappe
from frappe.core.doctype.scheduled_job_type.scheduled_job_type import insert_events
from frappe.tests.utils import FrappeTestCase
from selenium.common.exceptions import WebDriverException

from press.hooks import scheduler_events
from press.sanity import initialize_webdriver


class TestSanity(FrappeTestCase):
	def test_valid_scheduler_events(self):
		for event in insert_events(scheduler_events):
			frappe.get_attr(event)


class TestInitializeWebdriver(FrappeTestCase):
	"""The chromedriver mismatch recovery path, which runs during `bench migrate`.

	That path used to crash on any selenium message it did not recognise, reporting
	`'NoneType' object has no attribute 'group'` instead of the real cause.
	"""

	def drive_failure(self, message):
		"""Make `webdriver.Chrome` fail, and return the exception it raised."""
		with (
			patch("press.sanity.webdriver.Chrome", side_effect=WebDriverException(message)),
			patch("press.sanity.os.path.exists", return_value=True),
			patch("press.sanity.download_chromedriver") as download,
			self.assertRaises(WebDriverException) as raised,
		):
			initialize_webdriver()
		return raised.exception, download

	def test_unchrecognised_selenium_message_reraises_the_original_error(self):
		exception, download = self.drive_failure("session not created: no chrome binary")

		self.assertIn("no chrome binary", str(exception))
		download.assert_not_called()

	def test_none_selenium_message_reraises_the_original_error(self):
		exception, download = self.drive_failure(None)

		self.assertIsInstance(exception, WebDriverException)
		download.assert_not_called()

	def test_parsable_chromedriver_version_triggers_a_download(self):
		# The wording `initialize_webdriver` looks for: "is <version> with".
		_, download = self.drive_failure(
			"session not created: the driver is 131.0.6778.85 with Chrome version 131"
		)

		download.assert_called_once_with(version="131.0.6778.85")
