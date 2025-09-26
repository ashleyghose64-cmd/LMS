import streamlit as st
import sqlite3

conn = sqlite3.connect("lms.db", check_same_thread=False)
c = conn.cursor()

st.set_page_config(page_title="Admin Panel", layout="wide")
st.markdown("""
<style>
body { background-color: white; }
h1,h2,h3,h4,h5 { font-family: 'Helvetica Neue', sans-serif; color:#222; }
.stButton>button { border-radius: 10px; padding: 8px 20px; font-size:16px; background-color:#4CAF50; color:white; margin:4px 0;}
</style>
""", unsafe_allow_html=True)

st.title("🛠 Admin Dashboard")

# -------------------- VIEW USERS --------------------
st.subheader("👥 Users")
users = c.execute("SELECT username, role FROM users").fetchall()
for u in users:
    st.write(f"Username: {u[0]}, Role: {u[1]}")

# -------------------- VIEW MATERIALS --------------------
st.subheader("📂 Materials")
materials = c.execute("SELECT teacher, title, filename FROM materials").fetchall()
for m in materials:
    st.write(f"Title: {m[1]}, Teacher: {m[0]}")
    st.download_button(
        "Download",
        open(m[2], "rb"),
        file_name=m[2].split("/")[-1],
        key=f"mat_{m[1]}"
    )

# -------------------- VIEW EVENTS --------------------
st.subheader("📅 Calendar Events")
events = c.execute("SELECT title, start, end, teacher FROM events").fetchall()
for e in events:
    st.write(f"{e[0]} ({e[3]}): {e[1]} → {e[2]}")

# -------------------- VIEW ASSIGNMENTS --------------------
st.subheader("📤 Assignments")
assignments = c.execute("SELECT student, filename, grade FROM assignments").fetchall()
for a in assignments:
    st.write(f"Student: {a[0]}, File: {a[1]}, Grade: {a[2]}")
