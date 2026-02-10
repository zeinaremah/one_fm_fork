# Copyright (c) 2025, ONE FM and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMethod(FrappeTestCase):
	def tearDown(self):
		"""Clean up any test Method records"""
		# Delete test methods if they exist
		test_methods = ["test_method_invalid", "one_fm.test.valid_method"]
		for method_name in test_methods:
			if frappe.db.exists("Method", method_name):
				frappe.delete_doc("Method", method_name, force=True)
	
	def test_method_validation_requires_dotted_path(self):
		"""Test that Method validation requires a dotted path"""
		# Test with invalid method path (no dots)
		method_doc = frappe.get_doc({
			"doctype": "Method",
			"method": "invalid_method_name",
			"document_type": "Task",
			"description": "Test invalid method"
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError) as cm:
			method_doc.insert()
		
		self.assertIn("dotted path", str(cm.exception).lower())
	
	def test_method_validation_requires_existing_method(self):
		"""Test that Method validation checks if method exists"""
		# Test with valid format but non-existent method
		method_doc = frappe.get_doc({
			"doctype": "Method",
			"method": "one_fm.test.nonexistent_method",
			"document_type": "Task",
			"description": "Test non-existent method"
		})
		
		# Should raise validation error
		with self.assertRaises(frappe.ValidationError) as cm:
			method_doc.insert()
		
		# Error should mention inability to import
		self.assertIn("cannot import", str(cm.exception).lower())
	
	def test_method_validation_accepts_valid_path(self):
		"""Test that Method validation accepts valid paths"""
		# Use an existing frappe method as example
		method_doc = frappe.get_doc({
			"doctype": "Method",
			"method": "frappe.utils.now",  # This is a valid frappe method
			"document_type": "Task",
			"description": "Test valid method"
		})
		
		# Should not raise any error
		try:
			method_doc.insert()
			# Verify it was created
			self.assertTrue(frappe.db.exists("Method", "frappe.utils.now"))
		finally:
			# Clean up
			if frappe.db.exists("Method", "frappe.utils.now"):
				frappe.delete_doc("Method", "frappe.utils.now", force=True)
