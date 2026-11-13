import queue, threading, uuid
from fastapi import FastAPI, HTTPException
from ingest import run_ingest

app = FastAPI(title="Ingestion API")
jobs = queue.Queue()
tasks = {}


def worker():
    while True:
        task_id = jobs.get()
        tasks[task_id]["status"] = "STARTED"
        try:
            tasks[task_id]["result"] = run_ingest()
            tasks[task_id]["status"] = "SUCCESS"
        except Exception as e:
            tasks[task_id].update(status="FAILURE", error=str(e))
        jobs.task_done()


threading.Thread(target=worker, daemon=True).start()


@app.post("/ingest", status_code=202)
def ingest():
    task_id = uuid.uuid4().hex
    tasks[task_id] = {"status": "PENDING"}
    jobs.put(task_id)
    return {"task_id": task_id}          # returns instantly, work happens in background


@app.get("/tasks/{task_id}")
def task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Unknown task id")
    return tasks[task_id]

#  uvicorn api:app --reload