import streamlit as st
import requests
import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Task Manager", layout="centered")
st.title("Task Manager (FastAPI + Streamlit)")

# ADD TASK
st.header("➕ Add Task")
title = st.text_input("Title")
description = st.text_area("Description")
priority = st.number_input("Priority", 1, 10, 1)
due_date = st.date_input("Due Date")

if st.button("Add Task"):
    res = requests.post(
        f"{API_URL}/tasks",
        json={
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": str(due_date)
        }
    )
    st.success(res.json()["message"])


# VIEW TASKS
st.header("📋 All Tasks")
if st.button("Refresh Tasks"):
    tasks = requests.get(f"{API_URL}/tasks").json()
    for t in tasks:
        st.write(f"**{t['title']}** | Priority: {t['priority']} | Status: {t['status']}")
        st.caption(t["description"])


# UPDATE PRIORITY
st.header("⬆ Update Priority")
up_title = st.text_input("Task Title (Priority)")
new_priority = st.number_input("New Priority", 1, 10)

if st.button("Update Priority"):
    res = requests.put(
        f"{API_URL}/tasks/{up_title}",
        params={"priority": new_priority}
    )
    st.info(res.json())


# UPDATE STATUS
st.header("🔄 Update Status")
status_title = st.text_input("Task Title (Status)")
status = st.selectbox("Status", ["pending", "in-progress", "completed"])

if st.button("Update Status"):
    res = requests.put(
        f"{API_URL}/tasks/{status_title}/status",
        params={"status": status}
    )
    st.success(res.json())


# SEARCH
st.header("🔍 Search Tasks")
query = st.text_input("Search by title")
filter_status = st.selectbox("Filter Status", ["", "pending", "in-progress", "completed"])

if st.button("Search"):
    res = requests.get(
        f"{API_URL}/tasks/search",
        params={"q": query, "status": filter_status or None}
    ).json()
    for t in res:
        st.write(t)


# RECOMMEND
st.header("✨ Recommended Tasks")
keyword = st.text_input("Keyword")

if st.button("Recommend"):
    res = requests.get(
        f"{API_URL}/recommend",
        params={"keyword": keyword}
    ).json()
    if res:
        for t in res:
            st.write(f"✅ {t['title']} - {t['description']}")
    else:
        st.info("No recommendations found")


# DELETE
st.header("🗑 Archive Task")
del_title = st.text_input("Task Title (Delete)")

if st.button("Archive"):
    res = requests.delete(f"{API_URL}/tasks/{del_title}")
    st.warning(res.json())


# LOGS
st.header("📜 Activity Logs")
if st.button("View Logs"):
    logs = requests.get(f"{API_URL}/logs").json()
    for log in logs:
        st.write("•", log)


# EXPORT
st.header("⬇ Export Tasks")
csv_data = requests.get(f"{API_URL}/export").content
st.download_button("Download CSV", csv_data, "tasks.csv")