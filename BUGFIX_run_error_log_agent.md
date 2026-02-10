# Fix for run_error_log_agent_from_task Error

## Error Description
```
frappe.exceptions.AppNotInstalledError: App run_error_log_agent_from_task is not installed
```

## Root Cause
A background job is being enqueued with an incorrect method name that lacks the module path:
- **Incorrect**: `"run_error_log_agent_from_task"`
- **Correct**: `"one_fm.events.error_log.run_error_log_agent_from_task"` or `"one_fm.run_error_log_agent_from_task"`

When Frappe's `get_attr()` function receives a method name without dots, it treats it as an app name, causing the error.

## Code Changes Made
1. **Added the missing function** in `/one_fm/events/error_log.py`:
   ```python
   def run_error_log_agent_from_task(doc):
       """Background task to handle Error Log processing."""
       # Implementation with error handling
   ```

2. **Exported function** in `/one_fm/__init__.py`:
   ```python
   from one_fm.events.error_log import run_error_log_agent_from_task
   ```
   
   This makes the function available at module level as `one_fm.run_error_log_agent_from_task`.

## Required Database-Level Fix
The enqueue source is NOT in code files - it's likely in one of these database configurations:

### Option 1: Check Server Scripts
```bash
# Via bench console
bench --site [site-name] console

# In Python console:
import frappe
scripts = frappe.get_all("Server Script", 
    filters={"reference_doctype": "Error Log"}, 
    fields=["name", "script_type", "script"])
for script in scripts:
    print(f"\nScript: {script.name}")
    print(f"Type: {script.script_type}")
    if "run_error_log_agent_from_task" in script.script:
        print("⚠️ FOUND - This script needs to be updated!")
        print(script.script)
```

### Option 2: Check Assignment Rules
```bash
# Via bench console
bench --site [site-name] console

# In Python console:
import frappe
rules = frappe.get_all("Assignment Rule", 
    filters={"document_type": "Error Log"}, 
    fields=["name", "assign_condition", "rule"])
for rule in rules:
    print(f"\nRule: {rule.name}")
    rule_doc = frappe.get_doc("Assignment Rule", rule.name)
    print(rule_doc.as_dict())
```

### Option 3: Check doc_events Hooks
```bash
# Via bench console
bench --site [site-name] console

# In Python console:
import frappe
from frappe.utils import get_hooks
hooks = get_hooks("doc_events")
error_log_hooks = hooks.get("Error Log", {})
print("Error Log hooks:", error_log_hooks)
```

### Option 4: Clear Failed Jobs from Queue
```bash
# Clear all failed jobs
bench --site [site-name] console

# In Python console:
import frappe
from rq import Queue
from frappe.utils.background_jobs import get_redis_conn

redis_conn = get_redis_conn()
failed_queue = Queue("failed", connection=redis_conn)
print(f"Failed jobs: {len(failed_queue)}")

# Clear all failed jobs
failed_queue.empty()
print("Failed queue cleared!")
```

## How to Fix the Database Configuration

Once you've identified where the incorrect enqueue call is coming from, update it:

**Before:**
```python
frappe.enqueue(
    "run_error_log_agent_from_task",
    job_name="run_error_log_agent_from_task",
    doc=doc
)
```

**After:**
```python
frappe.enqueue(
    "one_fm.events.error_log.run_error_log_agent_from_task",
    job_name="run_error_log_agent_from_task",
    doc=doc
)
```

OR (shorter version since we exported it in __init__.py):
```python
frappe.enqueue(
    "one_fm.run_error_log_agent_from_task",
    job_name="run_error_log_agent_from_task",
    doc=doc
)
```

## Verification Steps

After applying the fix:

1. **Clear the cache and restart**:
   ```bash
   bench --site [site-name] clear-cache
   bench --site [site-name] restart
   ```

2. **Create a test Error Log**:
   ```bash
   bench --site [site-name] console
   
   # In Python console:
   import frappe
   frappe.log_error("Test error", "Test Error Log Agent")
   ```

3. **Check if the background job succeeds**:
   ```bash
   # Monitor the RQ worker logs
   tail -f logs/worker.log
   ```

4. **Verify no more failures**:
   ```bash
   bench --site [site-name] console
   
   # In Python console:
   from rq import Queue
   from frappe.utils.background_jobs import get_redis_conn
   
   redis_conn = get_redis_conn()
   failed_queue = Queue("failed", connection=redis_conn)
   print(f"Failed jobs: {len(failed_queue)}")
   
   # Should be 0 or not contain run_error_log_agent_from_task errors
   ```

## Related Files
- `/one_fm/events/error_log.py` - Contains the function implementation
- `/one_fm/__init__.py` - Exports the function at module level
- `/one_fm/custom/custom_field/error_log.py` - Custom field for HD Ticket link
- `/one_fm/public/js/doctype_js/error_log.js` - Manual HD Ticket creation UI

## Related HD Ticket
- **Ticket**: [1259](http://one-fm.staging:8001/app/hd-ticket/1259)
- **Date**: 2025-12-14
- **Environment**: Staging

## Notes
- The function is currently a no-op (does nothing except log)
- Future implementations can add automatic HD Ticket creation or AI-based error analysis
- The manual HD Ticket creation via UI button still works as before
