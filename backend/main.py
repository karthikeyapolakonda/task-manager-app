from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import csv
from fastapi.responses import FileResponse

app = FastAPI(title="Task Manager API")

# MODELS
class Task(BaseModel):
    title: str
    description: str
    priority: int = 1
    status: str = "pending"
    due_date: Optional[date] = None
    is_deleted: bool = False


# STORAGE
tasks: List[Task] = []
activity_logs: List[str] = []


def log_action(action: str):
    activity_logs.append(action)


# ROUTES
@app.post("/tasks")
def add_task(task: Task):
    tasks.append(task)
    log_action(f"Task added: {task.title}")
    return {"message": "Task added successfully"}


@app.get("/tasks")
def list_tasks():
    return sorted(
        [t for t in tasks if not t.is_deleted],
        key=lambda t: t.priority
    )


@app.put("/tasks/{title}")
def update_priority(title: str, priority: int):
    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.priority = priority
            log_action(f"Priority updated for: {title}")
            return {"message": "Priority updated"}
    return {"error": "Task not found"}


@app.put("/tasks/{title}/status")
def update_status(title: str, status: str):
    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.status = status
            log_action(f"Status updated for: {title}")
            return {"message": "Status updated"}
    return {"error": "Task not found"}


@app.delete("/tasks/{title}")
def soft_delete(title: str):
    for task in tasks:
        if task.title.lower() == title.lower():
            task.is_deleted = True
            log_action(f"Task archived: {title}")
            return {"message": "Task archived"}
    return {"error": "Task not found"}


@app.get("/tasks/search")
def search_tasks(q: str = "", status: Optional[str] = None):
    result = [t for t in tasks if not t.is_deleted]

    if q:
        result = [t for t in result if q.lower() in t.title.lower()]

    if status:
        result = [t for t in result if t.status == status]

    return result


@app.get("/recommend")
def recommend(keyword: str):
    keyword_words = set(keyword.lower().split())
    recommended = []

    for task in tasks:
        if task.is_deleted:
            continue
        desc_words = set(task.description.lower().split())
        similarity = len(keyword_words & desc_words) / max(len(keyword_words), 1)
        if similarity >= 0.3:
            recommended.append(task)

    return recommended


@app.get("/logs")
def get_logs():
    return activity_logs


@app.get("/export")
def export_tasks():
    filename = "tasks.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Priority", "Status", "Due Date"])
        for t in tasks:
            if not t.is_deleted:
                writer.writerow([t.title, t.description, t.priority, t.status, t.due_date])

    return FileResponse(filename, media_type="text/csv", filename=filename)