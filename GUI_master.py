import tkinter as tk
from tkinter import ttk, messagebox as ms
import sqlite3
from PIL import Image, ImageTk
import os
from subprocess import call

# Initialize Main Window
root = tk.Tk()
root.configure(background="seashell2")
root.title("Online Exam Portal System")

# Get Screen Dimensions
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry(f"{w}x{h}+0+0")

# Background Image
try:
    background_image = Image.open('13.png').resize((1250, 950), Image.ANTIALIAS)  # Check file path
    background_photo = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(root, image=background_photo)
    background_label.place(x=300, y=0)
except FileNotFoundError:
    ms.showerror("Error", "Background image '13.png' not found.")
    
# Add Logo at Top Right
try:
    logo_image = Image.open('ll.png').resize((200, 200), Image.ANTIALIAS)  # Adjust size as needed
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg="seashell2")
    logo_label.place(x=w-300, y=60)  # Position logo near the top-right corner
except FileNotFoundError:
    ms.showerror("Error", "Logo image 'logo.png' not found.")

# Marquee Function
def shift():
    x1, y1, x2, y2 = canvas.bbox("marquee")
    if x2 < 0:  # Reset the text position to start from the right
        canvas.coords("marquee", canvas.winfo_width(), y1)
    else:
        canvas.move("marquee", -2, 0)  # Move text to the left
    canvas.after(1000 // fps, shift)

# Create Canvas for Marquee
canvas = tk.Canvas(root, bg="#f5f5f5", height=40, width=1600, highlightthickness=0)
canvas.pack(fill=tk.X, pady=0)

# Add Text to the Canvas
text_var = "Welcome to the Online Exam Proctoring System"
text = canvas.create_text(0, 20, text=text_var, font=("Raleway", 16, "italic"), fill="#13919b", anchor='w', tags=("marquee",))

# Set Frames Per Second (FPS)
fps = 40

# Start the Marquee Animation
shift()



# Create Frame for Buttons
frame_alpr = tk.Frame(root, bg="#20a7db", relief=tk.RIDGE, bd=10)
frame_alpr.place(x=0, y=40, width=300, height=900)

# Create Database
def create_database():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    roll_number TEXT PRIMARY KEY,
                    seat_number TEXT,
                    student_name TEXT
                 )''')
    conn.commit()
    conn.close()

create_database()

# Add Student Details
def add_student_details():
    def submit_details():
        student_name = entry_name.get()
        roll_number = entry_roll.get()
        seat_number = entry_seat.get()
        
        if student_name == "" or roll_number == "" or seat_number == "":
            ms.showerror("Error", "All fields are required")
        else:
            conn = sqlite3.connect('students.db')
            c = conn.cursor()

            c.execute("SELECT * FROM students WHERE roll_number = ?", (roll_number,))
            existing_student = c.fetchone()

            if existing_student:
                ms.showerror("Error", "Roll Number already exists!")
            else:
                c.execute("INSERT INTO students (roll_number, seat_number, student_name) VALUES (?, ?, ?)", 
                          (roll_number, seat_number, student_name))
                conn.commit()
                ms.showinfo("Success", "Student details saved successfully")

            conn.close()
            add_student_window.destroy() 
    
    add_student_window = tk.Toplevel(root)
    add_student_window.title("Add Student Details")
    add_student_window.geometry("500x300")
    add_student_window.configure(background="seashell2")

    tk.Label(add_student_window, text="Student Name:", font=('times', 12), bg="seashell2").place(x=10, y=20)
    entry_name = tk.Entry(add_student_window, font=('times', 12), width=25)
    entry_name.place(x=120, y=20)

    tk.Label(add_student_window, text="Roll Number:", font=('times', 12), bg="seashell2").place(x=10, y=60)
    entry_roll = tk.Entry(add_student_window, font=('times', 12), width=25)
    entry_roll.place(x=120, y=60)

    tk.Label(add_student_window, text="Seat Number:", font=('times', 12), bg="seashell2").place(x=10, y=100)
    entry_seat = tk.Entry(add_student_window, font=('times', 12), width=25)
    entry_seat.place(x=120, y=100)

    tk.Button(add_student_window, text="Submit", command=submit_details, width=20, height=1,
              font=('times', 15, 'bold'), bg="yellow4", fg="white").place(x=10, y=160)

# Launch Exam
def launch_exam(subject):
    def open_exam_rules():
        def submit_terms():
            if not terms_checkbox_var.get():
                ms.showerror("Error", "You must accept the terms and conditions to proceed.")
            else:
                open_exam_portal(subject)
                exam_rules_window.destroy()

        exam_rules_window = tk.Toplevel(root)
        exam_rules_window.title(f"{subject} Exam Rules")
        exam_rules_window.geometry("800x600")
        exam_rules_window.configure(background="#b8c2fe")

        rules_text = ("Please read the following rules before starting the exam:\n\n"
                      "1. No cheating allowed.\n"
                      "2. Keep your camera on during the exam.\n"
                      "3. Ensure stable internet.\n"
                      "4. No unauthorized materials.\n")
        tk.Label(exam_rules_window, text=rules_text, font=('times', 12), bg="#b8c2fe", justify="left").pack(pady=20)

        terms_checkbox_var = tk.BooleanVar()
        tk.Checkbutton(exam_rules_window, text="I accept the terms and conditions", variable=terms_checkbox_var, bg="#b8c2fe").pack(pady=10)

        tk.Button(exam_rules_window, text="Submit", command=submit_terms, width=20, height=1,
                  font=('times', 15, 'bold'), bg="#b8c2fe", fg="black").pack(pady=20)

    def open_exam_portal(subject):
        script_name = f"{subject.lower()}_paper.py"
        if os.path.exists(script_name):
            call(["python", script_name])
        else:
            ms.showerror("Error", f"{subject} exam script not found!")

    open_exam_rules()

# Exit Application
def exit_app():
    root.destroy()

# Buttons and Combobox
tk.Button(frame_alpr, text="Add Student Details", command=add_student_details, width=20, height=1,
          font=('times', 15, 'bold'), bg="#E6E6FA", fg="black").place(x=10, y=50)

tk.Label(frame_alpr, text="Select Subject:", font=('times', 15, 'bold'), bg="#20a7db").place(x=10, y=150)
combo_subject = ttk.Combobox(frame_alpr, font=('times', 15), width=20)
combo_subject['values'] = ('Python', 'Java', 'C++')
combo_subject.place(x=10, y=200)

tk.Button(frame_alpr, text="Start Exam", command=lambda: launch_exam(combo_subject.get()), width=20, height=1,
          font=('times', 15, 'bold'), bg="#E6E6FA", fg="black").place(x=10, y=300)

tk.Button(frame_alpr, text="Exit", command=exit_app, width=20, height=1,
          font=('times', 15, 'bold'), bg="#E6E6FA", fg="black").place(x=10, y=400)

root.mainloop()
