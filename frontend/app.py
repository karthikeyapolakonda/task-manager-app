import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Task Manager", layout="centered")
st.title("📝 Task Manager (FastAPI + Streamlit)")

# Add Task
st.header("Add Task")
title = st.text_input("Title")
description = st.text_area("Description")
priority = st.number_input("Priority", min_value=1, max_value=10, value=1)

if st.button("Add Task"):
    res = requests.post(
        f"{API_URL}/tasks",
        json={"title": title, "description": description, "priority": priority},
    )
    st.success(res.json()["message"])

# View Tasks
st.header("All Tasks")
if st.button("Refresh Tasks"):
    tasks = requests.get(f"{API_URL}/tasks").json()
    for t in tasks:
        st.write(f"🔹 **{t['title']}** (Priority {t['priority']})")
        st.caption(t["description"])

# Update Priority
st.header("Update Priority")
up_title = st.text_input("Task title to update")
new_priority = st.number_input("New Priority", min_value=1, max_value=10)

if st.button("Update"):
    res = requests.put(f"{API_URL}/tasks/{up_title}", params={"priority": new_priority})
    st.info(res.json())

# Delete Task
st.header("Remove Task")
del_title = st.text_input("Task title to delete")

if st.button("Delete"):
    res = requests.delete(f"{API_URL}/tasks/{del_title}")
    st.warning(res.json())

# Recommend
st.header("Recommended Tasks")
keyword = st.text_input("Keyword")

if st.button("Recommend"):
    res = requests.get(f"{API_URL}/recommend", params={"keyword": keyword}).json()
    if res:
        for t in res:
            st.write(f"✅ {t['title']} - {t['description']}")
    else:
        st.info("No recommendations found")