import streamlit as st

class Task:
    def __init__(self, title, description, priority=1):
        self.title = title
        self.description = description
        self.priority = priority

    def __str__(self):
        return f"[Priority {self.priority}] {self.title}: {self.description}"

class TaskManager:
    def __init__(self):
        if "tasks" not in st.session_state:
            st.session_state.tasks = []

    @property
    def tasks(self):
        return st.session_state.tasks

    def add_task(self, title, description, priority):
        self.tasks.append(Task(title, description, priority))

    def remove_task(self, title):
        self.tasks[:] = [t for t in self.tasks if t.title.lower() != title.lower()]

    def list_tasks(self):
        return sorted(self.tasks, key=lambda t: t.priority)

    def prioritize_task(self, title, new_priority):
        for task in self.tasks:
            if task.title.lower() == title.lower():
                task.priority = new_priority

    def recommend_tasks(self, keyword):
        keyword_words = set(keyword.lower().split())
        recommended = []

        for task in self.tasks:
            desc_words = set(task.description.lower().split())
            similarity = len(keyword_words & desc_words) / max(len(keyword_words), 1)
            if similarity >= 0.3:
                recommended.append(task)

        return recommended


# ---------------- UI ----------------

st.set_page_config(page_title="Task Manager", layout="centered")
st.title("🗂 Task Manager")

manager = TaskManager()

# ADD TASK
st.header("➕ Add Task")
title = st.text_input("Title")
description = st.text_area("Description")
priority = st.number_input("Priority", 1, 10, 1)

if st.button("Add Task"):
    manager.add_task(title, description, priority)
    st.success("Task added")

# LIST TASKS
st.header("📋 Tasks")
for task in manager.list_tasks():
    st.write(task)

# UPDATE PRIORITY
st.header("⬆ Update Priority")
p_title = st.text_input("Task title to update")
new_priority = st.number_input("New priority", 1, 10)

if st.button("Update Priority"):
    manager.prioritize_task(p_title, new_priority)
    st.success("Priority updated")

# RECOMMEND
st.header("✨ Recommendations")
keyword = st.text_input("Keyword")

if st.button("Recommend"):
    results = manager.recommend_tasks(keyword)
    if results:
        for task in results:
            st.write(task)
    else:
        st.info("No recommendations found")

# REMOVE
st.header("🗑 Remove Task")
r_title = st.text_input("Task title to remove")

if st.button("Remove"):
    manager.remove_task(r_title)
    st.warning("Task removed")
