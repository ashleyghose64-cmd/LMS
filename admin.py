import streamlit as st
import sqlite3

conn = sqlite3.connect("lms.db", check_same_thread=False)
c = conn.cursor()

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠 Admin Dashboard")

# -------------------- VIEW USERS --------------------
st.subheader("👥 Users")
users = c.execute("SELECT username, role, whatsapp_number FROM users").fetchall()
for u in users:
    st.write(f"{u[0]} | {u[1]} | {u[2]}")

# -------------------- VIEW ASSIGNMENTS --------------------
st.subheader("📝 Assignments")
assignments = c.execute("SELECT student, filename, grade FROM assignments").fetchall()
for a in assignments:
    st.write(f"{a[0]} | {a[1]} | {a[2]}")

# -------------------- VIEW MATERIALS --------------------
st.subheader("📂 Materials")
materials = c.execute("SELECT teacher, title, filename FROM materials").fetchall()
for m in materials:
    st.write(f"{m[1]} | {m[0]} | {m[2]}")

# -------------------- VIEW EVENTS --------------------
st.subheader("📅 Calendar Events")
events = c.execute("SELECT title, start, end, teacher FROM events").fetchall()
for e in events:
    st.write(f"{e[0]} | {e[1]} -> {e[2]} | {e[3]}")
