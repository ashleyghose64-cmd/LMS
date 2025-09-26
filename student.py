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
st.set_page_config(page_title="Student Portal", layout="wide")
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
    st.title("📚 Student Portal")
    option = st.radio("Select Option:", ["Login", "Register"], horizontal=True)

    if option == "Register":
        st.subheader("📝 Register New Student")
        reg_user = st.text_input("Username", key="reg_user")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            exists = c.execute("SELECT * FROM users WHERE username=?", (reg_user,)).fetchone()
            if exists:
                st.error("Username already exists!")
            else:
                c.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",
                          (reg_user, hash_password(reg_pass), "Student"))
                conn.commit()
                st.success("Registered successfully! You can now login.")

    elif option == "Login":
        st.subheader("🔑 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user = c.execute("SELECT * FROM users WHERE username=? AND password=? AND role='Student'",
                             (username, hash_password(password))).fetchone()
            if user:
                st.session_state.username = username
                st.success(f"Welcome {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password!")

# -------------------- STUDENT DASHBOARD --------------------
else:
    st.header(f"🎓 Welcome, {st.session_state.username}")

    # Materials
    st.subheader("📂 Study Materials")
    materials = c.execute("SELECT teacher, title, filename FROM materials").fetchall()
    for idx, m in enumerate(materials):
        st.write(f"{m[1]} (by {m[0]})")
        st.download_button(
            "Download",
            open(m[2], "rb"),
            file_name=os.path.basename(m[2]),
            key=f"mat_{idx}"
        )

    # Assignments
    st.subheader("📤 Submit Assignment")
    file = st.file_uploader("Upload Assignment", type=["pdf", "docx", "txt"], key="assign_up")
    if file and st.button("Submit"):
        os.makedirs("submissions", exist_ok=True)
        path = f"submissions/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        c.execute("INSERT INTO assignments (student, filename, grade) VALUES (?,?,?)",
                  (st.session_state.username, path, "Pending"))
        conn.commit()
        st.success("Assignment submitted!")

    # Calendar
    st.subheader("📅 Calendar")
    events = c.execute("SELECT title, start, end, teacher FROM events").fetchall()
    events_json = []
    colors = ["#4CAF50","#FF9800","#2196F3","#9C27B0","#F44336"]
    teacher_colors = {}
    idx_color = 0
    for e in events:
        teacher = e[3]
        if teacher not in teacher_colors:
            teacher_colors[teacher] = colors[idx_color % len(colors)]
            idx_color += 1
        events_json.append({
            "title": f"{e[0]} ({teacher})",
            "start": e[1],
            "end": e[2],
            "color": teacher_colors[teacher]
        })

    calendar_code = f"""
    <link href='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css' rel='stylesheet'/>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js'></script>
    <div id='calendar' style='background-color:white; padding:15px; border-radius:15px;
         box-shadow:0 2px 12px rgba(0,0,0,0.15); max-width:100%; margin:auto; font-family:"Helvetica Neue",sans-serif;'>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
      var calendarEl = document.getElementById('calendar');
      var calendar = new FullCalendar.Calendar(calendarEl, {{
        initialView: 'dayGridMonth',
        headerToolbar: {{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }},
        navLinks: true,
        editable: false,
        selectable: false,
        height: 'auto',
        contentHeight: 'auto',
        dayMaxEvents: true,
        events: {json.dumps(events_json)}
      }});
      calendar.render();
    }});
    </script>
    """
    components.html(calendar_code, height=600, scrolling=True)
