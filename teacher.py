import streamlit as st
import sqlite3
import json
import os
import streamlit.components.v1 as components
import hashlib

# -------------------- DB CONNECTION --------------------
conn = sqlite3.connect("lms.db", check_same_thread=False)
c = conn.cursor()

# -------------------- CREATE TABLES --------------------
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher TEXT,
    title TEXT,
    filename TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student TEXT,
    filename TEXT,
    grade TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start TEXT,
    end TEXT,
    teacher TEXT
)
""")
conn.commit()

# -------------------- SESSION --------------------
if "username" not in st.session_state:
    st.session_state.username = None

# -------------------- STYLING --------------------
st.set_page_config(page_title="Teacher Portal", layout="wide")
st.markdown("""
<style>
body { background-color: white; }
h1,h2,h3,h4,h5 { font-family: 'Helvetica Neue', sans-serif; color:#222; }
.stButton>button { border-radius: 10px; padding: 8px 20px; font-size:16px; background-color:#4CAF50; color:white; margin:5px 0;}
.stTextInput>div>input, .stDateInput>div>input { padding: 8px; border-radius:5px; border:1px solid #ddd; }
.stFileUploader>div>input { border-radius:5px; }
</style>
""", unsafe_allow_html=True)

# -------------------- PASSWORD HASH --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------- LOGIN / REGISTER --------------------
if st.session_state.username is None:
    st.title("👩‍🏫 Teacher Portal")
    option = st.radio("Select Option:", ["Login", "Register"], horizontal=True)

    if option == "Register":
        st.subheader("📝 Register New Teacher")
        reg_user = st.text_input("Username", key="reg_user")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            exists = c.execute("SELECT * FROM users WHERE username=?", (reg_user,)).fetchone()
           
