# Quick Fix Reference: run_error_log_agent_from_task

## Problem
```
frappe.exceptions.AppNotInstalledError: App run_error_log_agent_from_task is not installed
```

## Code Fix Status
✅ **COMPLETE** - Function implemented and exported

## Database Fix Required
⏳ **PENDING** - Admin action needed

## Quick Fix Steps (5 minutes)

### Step 1: Find the Bad Config
```bash
bench --site one-fm.staging console
```

```python
import frappe

# Check Server Scripts
scripts = frappe.get_all("Server Script", 
    filters={"reference_doctype": "Error Log"}, 
    fields=["name", "script"])
for s in scripts:
    if "run_error_log_agent_from_task" in (s.script or ""):
        print(f"FOUND in Server Script: {s.name}")
        
# Check Assignment Rules
rules = frappe.get_all("Assignment Rule", 
    filters={"document_type": "Error Log"},
    fields=["name"])
print(f"Assignment Rules for Error Log: {rules}")
```

### Step 2: Fix the Method Path
Change this:
```python
frappe.enqueue("run_error_log_agent_from_task", ...)
```

To this:
```python
frappe.enqueue("one_fm.run_error_log_agent_from_task", ...)
```

### Step 3: Clear Failed Jobs
```bash
bench --site one-fm.staging console
```

```python
from rq import Queue
from frappe.utils.background_jobs import get_redis_conn

redis_conn = get_redis_conn()
failed = Queue("failed", connection=redis_conn)
print(f"Clearing {len(failed)} failed jobs...")
failed.empty()
print("✓ Done!")
```

### Step 4: Test
```bash
bench --site one-fm.staging console
```

```python
import frappe
frappe.log_error("Test", "Test Agent")
# Check worker logs - should succeed now
```

## Files Modified
- `/one_fm/events/error_log.py` - Function implementation
- `/one_fm/__init__.py` - Module export
- `/BUGFIX_run_error_log_agent.md` - Full documentation

## Support
See `BUGFIX_run_error_log_agent.md` for detailed instructions
