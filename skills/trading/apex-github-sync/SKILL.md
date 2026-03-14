---
name: apex-github-sync
description: Syncs APEX skills between local Hermes installation and GitHub repository. Enables version control, backup, and cross-platform deployment.
triggers:
  - schedule: "0 2 * * 0"  # Sunday 2 AM - weekly sync
tags: [apex, trading, github, sync, backup, version-control]
---

# APEX GitHub Sync

## Purpose
Keeps local APEX skills synchronized with GitHub repository for:
- Version control and rollback
- Cross-platform deployment
- Backup and disaster recovery
- Sharing with other agents

## Configuration

Create `~/.apex/github_config.json`:

```json
{
  "repo": "sn-sujay/apex-trading-skills",
  "branch": "main",
  "auto_push": true,
  "auto_pull": false,
  "sync_on_change": true,
  "backup_before_push": true
}
```

## Commands

### Push Local to GitHub
```python
load_skill("apex-github-sync")
# Runs: push_local_to_github()
```

### Pull GitHub to Local
```python
load_skill("apex-github-sync")
# Runs: pull_github_to_local()
```

### Check Sync Status
```python
status = get_sync_status()
print(status)
```
