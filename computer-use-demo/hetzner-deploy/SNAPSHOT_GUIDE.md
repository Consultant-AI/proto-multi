# Snapshot Best Practices Guide

## Why Snapshots Can Be Slow to Restore

**The Problem:**
Hetzner snapshots save disk contents but NOT running Docker containers. When you restore a snapshot:

1. ✅ Server boots quickly (~30 seconds)
2. ❌ Docker needs to rebuild/restart containers (5-15 minutes)

**Why This Happens:**
- Docker images are stored in overlay filesystems
- Running containers aren't persisted in snapshots
- If Docker images aren't fully built when you snapshot, they rebuild on restore

## How to Create FAST Snapshots

### Step 1: Wait for Services to Be Ready

**IMPORTANT:** Only create snapshots when services are fully running!

```
Dashboard → Wait for "Services Ready" ✅ green indicator
```

This ensures:
- ✅ Docker images are fully built
- ✅ All containers have started successfully
- ✅ Application is fully deployed

### Step 2: Create the Snapshot

Once you see "Services Ready":

1. Click **"💾 Snapshot"** button
2. (Optional) Enter description or leave blank for auto-naming
3. Click **"Create Snapshot"**
4. Wait ~30 seconds

### Step 3: Verify Snapshot is Ready

```
Dashboard → Snapshots section
```

You should see:
- Snapshot with timestamp
- Size: ~5-10 GB (includes Docker images)
- Status: Available

## Restoring from Fast Snapshots

When you restore from a properly created snapshot:

```
Create Instance → Select Snapshot → Create
```

**Timeline:**
1. Server creation: ~30 seconds ✅
2. Docker starts existing containers: ~1-2 minutes ✅
3. **Total: ~2-3 minutes** (vs 10-15 for fresh build)

## Common Mistakes

### ❌ Snapshotting Too Early

**Problem:** Creating snapshot while services are still building

```
Instance Status: "Services Starting..."
↓
Create Snapshot ❌ BAD
↓
Restore takes 10-15 min (rebuilds everything)
```

**Solution:** Wait for "Services Ready" ✅

### ❌ Snapshotting Stopped Instances

**Problem:** Creating snapshot of stopped/paused instance

When you stop an instance:
- Docker containers are stopped
- May lose in-memory state
- Restore requires restart (slower)

**Solution:** Snapshot running instances with active containers

## Workflow for Maximum Cost Savings

### Recommended: Snapshot + Delete

Use the **"💾🗑️ Snapshot + Delete"** button:

1. Creates snapshot while services are running ✅
2. Deletes instance to stop billing ✅
3. Keeps snapshot for ~€0.10-0.30/month ✅

**Savings:**
- Running instance: ~€7/month
- Snapshot only: ~€0.20/month
- **Save: ~€6.80/month**

### When You Need It Again

1. Create new instance from snapshot
2. Wait ~2-3 minutes for services to start
3. Use normally
4. When done: Snapshot + Delete again

## Technical Details

### What's Saved in a Snapshot

✅ **Included:**
- All files on disk
- Installed packages (Docker, nginx, etc.)
- Built Docker images (if containers were running)
- Configuration files
- Docker volumes

❌ **Not Included:**
- Running processes
- In-memory state
- Temporary files in /tmp
- Active network connections

### Docker Image Persistence

**When Services Are Ready:**
```bash
# Docker images are saved in /var/lib/docker
# Containers can be restarted quickly:
docker compose up -d  # ~1-2 minutes
```

**When Services Not Ready:**
```bash
# Docker images incomplete or missing
# Must rebuild:
docker build ...      # ~5-10 minutes
docker compose up -d  # ~1-2 minutes
# Total: 10-15 minutes
```

## Cost Comparison

| Scenario | Monthly Cost | Restore Time |
|----------|-------------|--------------|
| Keep instance running | ~€7.00 | Instant |
| Stop instance (not deleted) | ~€7.00 | ~2 min |
| Delete + Fast snapshot | ~€0.20 | ~2-3 min |
| Delete + Slow snapshot | ~€0.20 | ~10-15 min |
| Delete (no snapshot) | €0.00 | ~10-15 min |

## Troubleshooting

### Snapshot Restore Still Slow?

**Check:**

1. **Was instance "Services Ready" when snapshotted?**
   - If no: Snapshot doesn't have built Docker images
   - Solution: Create new snapshot from ready instance

2. **Check snapshot size:**
   ```
   Dashboard → Snapshots
   ```
   - Small (~2-3 GB): Likely missing Docker images ❌
   - Larger (~5-10 GB): Has Docker images ✅

3. **Server type changed?**
   - Old snapshots from `cx22` (deprecated)
   - New instances use `cpx22`
   - May cause compatibility issues

### Warning During Snapshot Creation

If you see:
```
⚠️ Services not ready - snapshot may require rebuild on restore
```

This means:
- Instance was snapshotted too early
- Restored instance will be slower
- Recommendation: Wait for services to be ready and create new snapshot

## Best Practices Summary

1. ✅ **Always wait for "Services Ready"** before snapshotting
2. ✅ **Use "Snapshot + Delete"** to save maximum money
3. ✅ **Name snapshots** with descriptive names or use auto-naming
4. ✅ **Delete old snapshots** you no longer need
5. ✅ **Test restore** to verify snapshot works correctly
6. ❌ **Don't snapshot** instances that are still building
7. ❌ **Don't keep** unused running instances (use snapshots instead)

## Example Workflow

### Daily Development

**Morning:**
```
1. Create instance from snapshot (~2-3 min)
2. Work on project
```

**Evening:**
```
3. Snapshot + Delete (~30 sec + deletion)
4. Pay only for snapshot (~€0.20/month)
```

### Cost Savings
- Running 24/7: ~€210/month (30 days)
- Running 8h/day: ~€70/month
- Snapshot + Delete: ~€0.20/month + €2.33/month (8h/day) = ~€2.53/month
- **Savings: ~€207/month (98%)**

## Additional Tips

### Multiple Snapshots

You can keep multiple snapshots:
- `snapshot-working-setup` - Known good configuration
- `snapshot-experiment-1` - Testing new features
- `snapshot-production` - Production-ready version

Each costs ~€0.20-0.30/month

### Snapshot Naming Convention

Recommended format:
```
project-purpose-YYYY-MM-DD

Examples:
computer-use-prod-2025-11-02
computer-use-test-2025-11-02
computer-use-backup-2025-11-01
```

Or use auto-naming:
```
snapshot-2025-11-02_14-30-00
```

### Deleting Snapshots

When you no longer need a snapshot:
```
Dashboard → Snapshots → 🗑️ Delete
```

This stops billing for that snapshot immediately.
