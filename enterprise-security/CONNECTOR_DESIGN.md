# Google Drive Connector: Design

**Source:** Google Drive folder "Company Policies" via a read-only service account.

**Sync schedule**
- Incremental sync every 15 minutes (Celery beat or cron).
- Full resync every night at 02:00 to catch missed changes and deletions.

**last_synced_at logic**
1. Read `last_synced_at` for this connector from the `sync_state` table (first run: 0).
2. Record `started = now()`.
3. Ask Drive for files with `modifiedTime > last_synced_at` (or use the Changes API page token).
4. For each changed file: compare the content hash; if different, delete its old chunks and re-index.
5. Files removed or trashed in Drive: delete their chunks.
6. Only after all files succeed, save `last_synced_at = started`. If the run fails, the old value
   is kept, so the next run retries the same window. Nothing is skipped.

**Security**
- Drive file permissions are mapped to `allowed_roles` on every chunk (e.g. the HR folder -> ["hr","admin"]).
- Permission changes count as changes and trigger re-indexing of that file.
- Credentials are stored in `.env`, never in code.

**Failures:** retry 3 times with backoff; alert when `now() - last_synced_at` is over 1 hour.