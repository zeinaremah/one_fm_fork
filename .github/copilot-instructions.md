## Branch Selection Rules

Check the issue labels to determine which branch to work on:

- **Label `hotfix`** → Branch: `version-15` (Critical production fixes)
- **Label `bug`** → Branch: `staging` (Non-critical staging fixes)

**Always**:
1. Create a feature branch FROM the target branch
2. Make your fix on that feature branch
3. Create a PR to merge back into the target branch (not main/default)
