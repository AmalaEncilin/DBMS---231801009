import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Akshayaa2005@",
    database="school_db"
)

cursor = db.cursor()

# Global variables for entry fields
entry_new_student_username = None
entry_new_student_password = None

# Login function
def login():
    username = entry_username.get()
    password = entry_password.get()

    cursor.execute("SELECT id, role FROM users WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()

    if result:
        user_id, role = result
        if role == 'student':
            open_student_page(user_id)
        elif role == 'teacher':
            open_teacher_page()
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Open Student Page
def open_student_page(student_id):
    student_window = tk.Toplevel(root)
    student_window.title("Student Page")
    student_window.geometry("400x300")
    student_window.configure(bg="#f0f4f7")

    ttk.Label(student_window, text="Attendance Records", font=("Helvetica", 14, "bold"), foreground="#333333").pack(pady=10)

    # Retrieve attendance records
    cursor.execute("SELECT date, status FROM attendance WHERE student_id=%s", (student_id,))
    records = cursor.fetchall()

    # Display attendance records in a table-like format
    frame = ttk.Frame(student_window)
    frame.pack(pady=10)
    if records:
        for record in records:
            ttk.Label(frame, text=f"Date: {record[0]}, Status: {record[1]}", font=("Helvetica", 11)).pack(anchor="w", padx=10)
    else:
        ttk.Label(student_window, text="No attendance records found.", font=("Helvetica", 11), foreground="gray").pack()

# Open Teacher Page
def open_teacher_page():
    global entry_new_student_username, entry_new_student_password  # Declare as global
    teacher_window = tk.Toplevel(root)
    teacher_window.title("Teacher Page")
    teacher_window.geometry("400x500")
    teacher_window.configure(bg="#f0f4f7")

    # Mark Attendance Section
    ttk.Label(teacher_window, text="Mark Attendance", font=("Helvetica", 14, "bold"), foreground="#333333").pack(pady=(10, 5))

    ttk.Label(teacher_window, text="Student ID:", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))
    entry_student_id = ttk.Entry(teacher_window, width=30)
    entry_student_id.pack(pady=5, padx=10)

    ttk.Label(teacher_window, text="Status (Present/Absent):", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))

    # Radio Buttons for Attendance Status
    attendance_status = tk.StringVar()
    attendance_status.set("Absent")  # default value

    ttk.Radiobutton(teacher_window, text="Present", variable=attendance_status, value="Present").pack(pady=5)
    ttk.Radiobutton(teacher_window, text="Absent", variable=attendance_status, value="Absent").pack(pady=5)

    # Add the Submit button to mark attendance
    ttk.Button(teacher_window, text="Submit", command=mark_attendance).pack(pady=10)

    # Separator line
    ttk.Separator(teacher_window, orient="horizontal").pack(fill="x", pady=10)

    # New Student Section
    ttk.Label(teacher_window, text="Add New Student", font=("Helvetica", 14, "bold"), foreground="#333333").pack(pady=10)

    ttk.Label(teacher_window, text="Username:", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))
    entry_new_student_username = ttk.Entry(teacher_window, width=30)
    entry_new_student_username.pack(pady=5, padx=10)

    ttk.Label(teacher_window, text="Password:", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))
    entry_new_student_password = ttk.Entry(teacher_window, width=30, show="*")
    entry_new_student_password.pack(pady=5, padx=10)

    # Button to add the new student
    ttk.Button(teacher_window, text="Add Student", command=add_student).pack(pady=10)

def mark_attendance():
    student_id = entry_student_id.get()
    status = attendance_status.get()
    today = date.today()

    # Check if the student_id exists in the users table with role 'student'
    cursor.execute("SELECT id FROM users WHERE id = %s AND role = 'student'", (student_id,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Student ID does not exist or is not a student")
        return

    # Insert the attendance record if student_id is valid
    try:
        cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                       (student_id, today, status))
        db.commit()
        messagebox.showinfo("Success", "Attendance marked successfully")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

def add_student():
    username = entry_new_student_username.get()
    password = entry_new_student_password.get()
    role = 'student'  # Since we're adding a new student, set role to 'student'

    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cursor.fetchone() is not None:
        messagebox.showerror("Error", "Username already exists. Please choose a different username.")
        return

    # Insert the new student record
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                       (username, password, role))
        db.commit()
        messagebox.showinfo("Success", "New student added successfully")
        # Clear entry fields after adding
        entry_new_student_username.delete(0, tk.END)
        entry_new_student_password.delete(0, tk.END)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))

# Main Window
root = tk.Tk()
root.title("Login")
root.geometry("350x300")
root.configure(bg="#f0f4f7")

ttk.Label(root, text="Login", font=("Helvetica", 16, "bold"), foreground="#333333").pack(pady=20)

ttk.Label(root, text="Username:", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))
entry_username = ttk.Entry(root, width=30)
entry_username.pack(pady=5, padx=10)

ttk.Label(root, text="Password:", font=("Helvetica", 11)).pack(anchor="w", padx=10, pady=(5, 0))
entry_password = ttk.Entry(root, width=30, show="*")
entry_password.pack(pady=5, padx=10)

ttk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()

# Close the database connection when done
cursor.close()
db.close()
