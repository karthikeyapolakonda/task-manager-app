from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Task Manager API")

class Task(BaseModel):
    title: str
    description: str
    priority: int = 1

tasks: List[Task] = []

@app.post("/tasks")
def add_task(task: Task):
    tasks.append(task)
    return {"message": "Task added successfully"}

@app.get("/tasks")
def list_tasks():
    return sorted(tasks, key=lambda t: t.priority)

@app.delete("/tasks/{title}")
def remove_task(title: str):
    for task in tasks:
        if task.title.lower() == title.lower():
            tasks.remove(task)
            return {"message": "Task removed"}
    return {"error": "Task not found"}

@app.put("/tasks/{title}")
def update_priority(title: str, priority: int):
    for task in tasks:
        if task.title.lower() == title.lower():
            task.priority = priority
            return {"message": "Priority updated"}
    return {"error": "Task not found"}

@app.get("/recommend")
def recommend(keyword: str):
    keyword_words = set(keyword.lower().split())
    recommended = []

    for task in tasks:
        desc_words = set(task.description.lower().split())
        similarity = len(keyword_words & desc_words) / max(len(keyword_words), 1)
        if similarity >= 0.3:
            recommended.append(task)

    return recommended