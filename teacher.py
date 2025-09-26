import streamlit as st
import sqlite3
import os
import datetime
import streamlit.components.v1 as components
import json

# -------------------- DB CONNECTION --------------------
conn = sqlite3.connect("lms.db", check_same_thread=False)
c = conn.cursor()

if "username" not in st.session_state:
    st.session_state.username = None

# -------------------- STYLING --------------------
st.set_page_config(page_title="Teacher Portal", layout="wide")
st.markdown("""
<style>
body { background-color: white; }
h1,h2,h3,h4,h5 { font-family: 'Helvetica Neue', sans-serif; color:#222; }
.stButton>button { border-radius: 10px; padding: 8px 20px; font-size:16px; background-color:#4CAF50; color:white; }
.stTextInput>div>input, .stDateInput>div>input { padding: 8px; border-radius:5px; border:1px solid #ddd; }
.stFileUploader>div>input { border-radius:5px; }
</style>
""", unsafe_allow_html=True)

# -------------------- LOGIN --------------------
if st.session_state.username is None:
    st.title("👩‍🏫 Teacher Portal")
    username = st.text_input("Username")
    if st.button("Login"):
        user = c.execute("SELECT * FROM users WHERE username=? AND role='Teacher'", (username,)).fetchone()
        if user:
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            st.experimental_rerun()
        else:
            st.error("Teacher not found!")

else:
    st.header(f"👩‍🏫 Welcome, {st.session_state.username}")

    # -------------------- Upload Material --------------------
    st.subheader("📂 Upload Material")
    title = st.text_input("Title", key="mat_title")
    file = st.file_uploader("Upload File", type=["pdf","docx","txt"], key="mat_file")
    if file and st.button("Upload Material"):
        os.makedirs("materials", exist_ok=True)
        path = f"materials/{file.name}"
        with open(path, "wb") as f:
            f.write(file.getbuffer())
        c.execute("INSERT INTO materials (teacher, title, filename) VALUES (?,?,?)",
                  (st.session_state.username, title, path))
        conn.commit()
        st.success("Material uploaded!")

    # -------------------- Calendar --------------------
    st.subheader("📅 Assign Subjects/Tasks")
    subj = st.text_input("Subject/Task", key="task_subj")
    start = st.date_input("Start Date", key="start_date")
    end = st.date_input("End Date", key="end_date")
    if st.button("Add Event"):
        c.execute("INSERT INTO events (title, start, end, teacher) VALUES (?,?,?,?)",
                  (subj, str(start), str(end), st.session_state.username))
        conn.commit()
        st.success("Event added!")

    # Show calendar
    st.subheader("📅 Calendar Overview")
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
    <div id='calendar' style='background-color:white; padding:15px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1);'></div>
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
        events: {json.dumps(events_json)}
      }});
      calendar.render();
    }});
    </script>
    """
    components.html(calendar_code, height=600)
