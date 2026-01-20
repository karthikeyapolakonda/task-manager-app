from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import csv
import os
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ MODELS ------------------

class Task(BaseModel):
    title: str
    description: str
    priority: int = 1
    status: str = "pending"
    due_date: Optional[date] = None
    is_deleted: bool = False


tasks: List[Task] = []
activity_logs: List[str] = []


def log_action(msg: str):
    activity_logs.append(msg)


# ------------------ PERSISTENCE ------------------

CSV_FILE = "tasks.csv"

def save_tasks():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Priority", "Status", "Due Date", "Is Deleted"])
        for t in tasks:
            writer.writerow([t.title, t.description, t.priority, t.status, t.due_date, t.is_deleted])


def load_tasks():
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                task = Task(
                    title=row["Title"],
                    description=row["Description"],
                    priority=int(row["Priority"]),
                    status=row["Status"],
                    due_date=row["Due Date"] if row["Due Date"] else None,
                    is_deleted=row["Is Deleted"].lower() == "true"
                )
                tasks.append(task)


@app.on_event("startup")
def startup_event():
    load_tasks()


# ------------------ ROUTES ------------------

@app.post("/tasks")
def add_task(task: Task):
    for t in tasks:
        if t.title.lower() == task.title.lower() and not t.is_deleted:
            raise HTTPException(status_code=400, detail="Task already exists")

    tasks.append(task)
    log_action(f"Task added: {task.title}")
    save_tasks()
    return {"message": "Task added successfully"}


@app.get("/tasks")
def list_tasks():
    return sorted(
        [t for t in tasks if not t.is_deleted],
        key=lambda x: x.priority
    )


@app.put("/tasks/{title}")
def update_priority(title: str, priority: int):
    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.priority = priority
            log_action(f"Priority updated: {title}")
            save_tasks()
            return {"message": "Priority updated successfully"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{title}/status")
def update_status(title: str, status: str):
    if status not in ["pending", "in-progress", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.status = status
            log_action(f"Status updated: {title}")
            save_tasks()
            return {"message": "Status updated successfully"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks/{title}")
def archive_task(title: str):
    for task in tasks:
        if task.title.lower() == title.lower():
            task.is_deleted = True
            log_action(f"Task archived: {title}")
            save_tasks()
            return {"message": "Task archived successfully"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.get("/tasks/search")
def search_tasks(q: str = "", status: Optional[str] = None):
    results = [t for t in tasks if not t.is_deleted]

    if q:
        results = [t for t in results if q.lower() in t.title.lower()]

    if status:
        results = [t for t in results if t.status == status]

    return results


@app.get("/recommend")
def recommend_tasks(keyword: str):
    keyword_words = set(keyword.lower().split())
    recommendations = []

    for task in tasks:
        if task.is_deleted:
            continue
        desc_words = set(task.description.lower().split())
        similarity = len(keyword_words & desc_words) / max(len(keyword_words), 1)
        if similarity >= 0.3:
            recommendations.append(task)

    return recommendations


@app.get("/logs")
def get_logs():
    return activity_logs


@app.get("/export")
def export_tasks():
    filename = "tasks.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Priority", "Status", "Due Date"])
        for t in tasks:
            if not t.is_deleted:
                writer.writerow([t.title, t.description, t.priority, t.status, t.due_date])

    return FileResponse(filename, media_type="text/csv", filename=filename)