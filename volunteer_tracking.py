import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Initialize connection to sqlite3 database
conn = sqlite3.connect('volunteers.db')
c = conn.cursor()

# Create tables if they don't exist
def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS volunteers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT NOT NULL,
                 role TEXT NOT NULL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS shifts (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 volunteer_id INTEGER NOT NULL,
                 shift_date TEXT NOT NULL,
                 shift_hours INTEGER NOT NULL,
                 task TEXT NOT NULL,
                 FOREIGN KEY (volunteer_id) REFERENCES volunteers (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 volunteer_id INTEGER NOT NULL,
                 date TEXT NOT NULL,
                 hours INTEGER NOT NULL,
                 FOREIGN KEY (volunteer_id) REFERENCES volunteers (id))''')
    
    conn.commit()

init_db()

# Helper functions
def add_volunteer(name, email, role):
    c.execute("INSERT INTO volunteers (name, email, role) VALUES (?, ?, ?)", (name, email, role))
    conn.commit()

def add_shift(volunteer_id, shift_date, shift_hours, task):
    c.execute("INSERT INTO shifts (volunteer_id, shift_date, shift_hours, task) VALUES (?, ?, ?, ?)", (volunteer_id, shift_date, shift_hours, task))
    conn.commit()

def log_attendance(volunteer_id, date, hours):
    c.execute("INSERT INTO attendance (volunteer_id, date, hours) VALUES (?, ?, ?)", (volunteer_id, date, hours))
    conn.commit()

def get_volunteers():
    c.execute("SELECT * FROM volunteers")
    return c.fetchall()

def get_shifts():
    c.execute("SELECT v.name, s.shift_date, s.shift_hours, s.task FROM shifts s JOIN volunteers v ON s.volunteer_id = v.id")
    return c.fetchall()

def get_attendance():
    c.execute("SELECT v.name, a.date, a.hours FROM attendance a JOIN volunteers v ON a.volunteer_id = v.id")
    return c.fetchall()

def get_volunteer_hours():
    c.execute("SELECT v.name, SUM(a.hours) as total_hours FROM attendance a JOIN volunteers v ON a.volunteer_id = v.id GROUP BY v.id")
    return c.fetchall()

# Streamlit app layout
st.title("Volunteer Scheduling and Tracking")

# Volunteer Sign-Up
st.header("Volunteer Sign-Up")
with st.form("volunteer_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.text_input("Role (e.g., Helper, Organizer)")
    submit_volunteer = st.form_submit_button("Add Volunteer")

    if submit_volunteer:
        add_volunteer(name, email, role)
        st.success(f"Volunteer {name} added successfully.")

# Shift Management
st.header("Shift Management")
volunteers = get_volunteers()
volunteer_dict = {f"{v[1]} ({v[3]})": v[0] for v in volunteers}  # Map name to id

with st.form("shift_form"):
    selected_volunteer = st.selectbox("Select Volunteer", list(volunteer_dict.keys()))
    shift_date = st.date_input("Shift Date")
    shift_hours = st.number_input("Shift Hours", min_value=1)
    task = st.text_input("Task")
    submit_shift = st.form_submit_button("Schedule Shift")

    if submit_shift:
        volunteer_id = volunteer_dict[selected_volunteer]
        add_shift(volunteer_id, shift_date, shift_hours, task)
        st.success(f"Shift scheduled for {selected_volunteer} on {shift_date}")

# Attendance Tracking
st.header("Attendance Tracking")
with st.form("attendance_form"):
    selected_volunteer_attendance = st.selectbox("Select Volunteer for Attendance", list(volunteer_dict.keys()))
    attendance_date = st.date_input("Attendance Date")
    attendance_hours = st.number_input("Hours Worked", min_value=1)
    submit_attendance = st.form_submit_button("Log Attendance")

    if submit_attendance:
        volunteer_id_attendance = volunteer_dict[selected_volunteer_attendance]
        log_attendance(volunteer_id_attendance, attendance_date, attendance_hours)
        st.success(f"Attendance logged for {selected_volunteer_attendance}")

# Live Shift Schedule
st.header("Live Shift Schedule")
shift_data = get_shifts()
shift_df = pd.DataFrame(shift_data, columns=["Volunteer", "Shift Date", "Hours", "Task"])
st.dataframe(shift_df)

# Attendance Record
st.header("Attendance Records")
attendance_data = get_attendance()
attendance_df = pd.DataFrame(attendance_data, columns=["Volunteer", "Date", "Hours"])
st.dataframe(attendance_df)

# Impact Reporting - Total Volunteer Hours
st.header("Impact Reporting - Total Volunteer Hours")
hours_data = get_volunteer_hours()
hours_df = pd.DataFrame(hours_data, columns=["Volunteer", "Total Hours"])
st.dataframe(hours_df)

# Close the connection to the database
conn.close()
