import os, json, time, datetime as dt

DRIVE = "sandbox_drive"          # stands in for a Google Drive folder
STATE = "sync_state.json"        # stores last_synced_at


def iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec="seconds")


def sync():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"last_synced_at": 0}
    started = time.time()
    changed = [f for f in sorted(os.listdir(DRIVE))
               if os.path.getmtime(os.path.join(DRIVE, f)) > state["last_synced_at"]]
    for f in changed:
        print(f"  re-index {f} (modified {iso(os.path.getmtime(os.path.join(DRIVE, f)))})")
    json.dump({"last_synced_at": started}, open(STATE, "w"))   # saved only after success
    print(f"synced {len(changed)} file(s) | last_synced_at = {iso(started)}")


def write(name, text):
    with open(os.path.join(DRIVE, name), "w") as f:
        f.write(text)


if __name__ == "__main__":
    os.makedirs(DRIVE, exist_ok=True)
    if os.path.exists(STATE):
        os.remove(STATE)
    write("policy.txt", "v1"); write("faq.txt", "v1")
    print("Sync 1:"); sync()
    print("Sync 2 (nothing changed):"); sync()
    time.sleep(1.2); write("faq.txt", "v2")
    print("Sync 3 (faq.txt changed):"); sync()