import frappe, json


@frappe.whitelist()
def create_issue_log(error_log):
    error_log = frappe._dict(json.loads(error_log))

    issue_log = frappe.get_doc({
        'doctype':'HD Ticket',
        'reference_doctype':error_log.doctype,
        'reference_name':error_log.name,
        'subject':error_log.method,
        'status':'Open',
        'description':error_log.error,
        'priority': 'High',
        'ticket_type': 'Bug',
    }).insert(ignore_permissions=True)
    issue_log.add_comment("Comment", error_log.error)
    frappe.db.set_value("Error Log", error_log.name, 'hd_ticket', issue_log.name)
    return issue_log.name


def run_error_log_agent_from_task(doc):
    """
    Background task to handle Error Log processing.
    This function is called asynchronously when an Error Log is created.
    
    Args:
        doc: Error Log document dict or object
    """
    try:
        # If doc is a dict, convert to frappe._dict for easier attribute access
        if isinstance(doc, dict):
            doc = frappe._dict(doc)
        
        # Skip processing if HD Ticket already exists
        if doc.get("hd_ticket"):
            return
        
        # For now, this is a no-op function to prevent the enqueue error.
        # Future implementations can add:
        # - Automatic HD Ticket creation for critical errors
        # - AI-based error analysis and classification
        # - Automatic assignment to relevant teams
        # - Notification to stakeholders
        
        frappe.logger().info(f"Error Log {doc.get('name')} processed by background agent")
        
    except Exception as e:
        # Log any errors that occur during processing, but don't fail
        frappe.log_error(
            message=frappe.get_traceback(),
            title=f"Error in run_error_log_agent_from_task for {doc.get('name', 'Unknown')}"
        )