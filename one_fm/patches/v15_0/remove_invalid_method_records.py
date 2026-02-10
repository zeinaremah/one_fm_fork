import frappe


def execute():
	"""
	Remove invalid Method records that don't have proper dotted paths.
	
	Valid method paths should be in the format: 
	- module.file.function (e.g., "one_fm.tasks.send_reminders")
	- app.module.file.function (e.g., "one_fm.api.tasks.process_data")
	
	Invalid paths like "run_error_log_agent_from_task" cause errors when Frappe
	tries to execute them as they're missing the app/module prefix.
	"""
	# Find all Method records
	methods = frappe.get_all("Method", fields=["name", "method", "document_type"])
	
	invalid_methods = []
	for method_doc in methods:
		method_path = method_doc.get("method")
		
		# Check if method path has at least one dot (indicating module.function format)
		if not method_path or "." not in method_path:
			invalid_methods.append(method_doc.name)
			frappe.logger().warning(
				f"Found invalid Method record: {method_doc.name} - "
				f"Method path '{method_path}' is not a valid dotted path"
			)
	
	# Delete invalid Method records and related Process Tasks
	for method_name in invalid_methods:
		try:
			# First, deactivate and clear any Process Tasks using this method
			process_tasks = frappe.get_all(
				"Process Task",
				filters={"method": method_name, "is_active": 1},
				fields=["name"]
			)
			
			for pt in process_tasks:
				try:
					pt_doc = frappe.get_doc("Process Task", pt.name)
					# Deactivate to prevent execution
					pt_doc.is_active = 0
					pt_doc.method = ""
					pt_doc.save(ignore_permissions=True)
					
					frappe.logger().info(
						f"Deactivated Process Task {pt.name} which referenced invalid method {method_name}"
					)
				except Exception as e:
					frappe.logger().error(
						f"Failed to deactivate Process Task {pt.name}: {str(e)}"
					)
					continue
			
			# Delete the invalid Method record
			frappe.delete_doc("Method", method_name, force=True, ignore_permissions=True)
			frappe.logger().info(f"Deleted invalid Method record: {method_name}")
			
		except Exception as e:
			frappe.logger().error(f"Failed to delete Method {method_name}: {str(e)}")
			continue
	
	# Commit changes
	if invalid_methods:
		frappe.db.commit()
		frappe.logger().info(
			f"Cleanup complete. Removed {len(invalid_methods)} invalid Method records"
		)
