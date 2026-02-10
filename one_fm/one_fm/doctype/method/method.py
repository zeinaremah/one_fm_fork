# Copyright (c) 2025, ONE FM and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Method(Document):
	def validate(self):
		"""Validate that the method field contains a valid dotted path"""
		self.validate_method_path()
	
	def validate_method_path(self):
		"""
		Ensure method path is a valid Python dotted path.
		
		Valid formats:
		- module.function (e.g., "tasks.send_email")
		- app.module.function (e.g., "one_fm.tasks.send_email")
		- app.module.file.function (e.g., "one_fm.api.tasks.process_data")
		
		Invalid formats:
		- "send_email" (no module)
		- "run_error_log_agent_from_task" (no module/app prefix)
		"""
		if not self.method:
			frappe.throw(_("Method path is required"))
		
		# Check if method has at least one dot (module.function format)
		if "." not in self.method:
			frappe.throw(
				_("Method path must be a valid Python dotted path. "
				  "Example: 'one_fm.tasks.send_email' or 'module.function'. "
				  "Got: '{0}'").format(self.method)
			)
		
		# Verify the method can be imported
		try:
			frappe.get_attr(self.method)
		except (ImportError, AttributeError, frappe.AppNotInstalledError) as e:
			frappe.throw(
				_("Cannot import method '{0}'. Please ensure the method exists and the path is correct. Error: {1}")
				.format(self.method, str(e))
			)
