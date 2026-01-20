from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
import csv
import os
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MODELS

class Task(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
    priority: int = Field(default=1, ge=1, le=10)
    status: str = Field(default="pending")
    due_date: Optional[date] = None
    is_deleted: bool = False


tasks: List[Task] = []
activity_logs: List[str] = []

CSV_FILE = "tasks.csv"

# ------------------ UTILS ------------------

def log_action(msg: str):
    activity_logs.append(f"{datetime.now()} - {msg}")

def save_tasks():
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Priority", "Status", "Due Date", "Is Deleted"])
        for t in tasks:
            writer.writerow([
                t.title,
                t.description,
                t.priority,
                t.status,
                t.due_date.isoformat() if t.due_date else "",
                t.is_deleted
            ])

def load_tasks():
    if not os.path.exists(CSV_FILE):
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(Task(
                title=row["Title"],
                description=row["Description"],
                priority=int(row["Priority"]),
                status=row["Status"],
                due_date=date.fromisoformat(row["Due Date"]) if row["Due Date"] else None,
                is_deleted=row["Is Deleted"].lower() == "true"
            ))

@app.on_event("startup")
def startup_event():
    tasks.clear()
    load_tasks()

# ------------------ ROUTES ------------------

@app.post("/tasks")
def add_task(task: Task):
    if any(t.title.lower() == task.title.lower() and not t.is_deleted for t in tasks):
        raise HTTPException(status_code=400, detail="Task already exists")

    tasks.append(task)
    log_action(f"Task added: {task.title}")
    save_tasks()
    return {"message": "Task added successfully"}

@app.get("/tasks", response_model=List[Task])
def list_tasks():
    return sorted(
        [t for t in tasks if not t.is_deleted],
        key=lambda x: x.priority
    )

@app.put("/tasks/{title}/priority")
def update_priority(title: str, priority: int = Query(..., ge=1, le=10)):
    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.priority = priority
            log_action(f"Priority updated: {title}")
            save_tasks()
            return {"message": "Priority updated"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{title}/status")
def update_status(title: str, status: str):
    if status not in {"pending", "in-progress", "completed"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.status = status
            log_action(f"Status updated: {title}")
            save_tasks()
            return {"message": "Status updated"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{title}")
def archive_task(title: str):
    for task in tasks:
        if task.title.lower() == title.lower() and not task.is_deleted:
            task.is_deleted = True
            log_action(f"Task archived: {title}")
            save_tasks()
            return {"message": "Task archived"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/search", response_model=List[Task])
def search_tasks(q: str = "", status: Optional[str] = None):
    results = [t for t in tasks if not t.is_deleted]

    if q:
        results = [t for t in results if q.lower() in t.title.lower()]
    if status:
        results = [t for t in results if t.status == status]

    return results

@app.get("/recommend", response_model=List[Task])
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
    filename = "export_tasks.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Description", "Priority", "Status", "Due Date"])
        for t in tasks:
            if not t.is_deleted:
                writer.writerow([
                    t.title,
                    t.description,
                    t.priority,
                    t.status,
                    t.due_date.isoformat() if t.due_date else ""
                ])

    return FileResponse(filename, media_type="text/csv", filename=filename)