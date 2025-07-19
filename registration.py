import tkinter as tk
from tkinter import messagebox as ms
import sqlite3
from tkinter import ttk
import cv2
import os
from PIL import Image, ImageTk
import numpy as np
import re
import subprocess

# Create the main window
window = tk.Tk()
window.geometry("1600x800")
window.title("REGISTRATION FORM")
window.configure(background="grey")

# Define variables
Fullname = tk.StringVar()
address = tk.StringVar()
college_name = tk.StringVar()
userid = tk.IntVar()
Email = tk.StringVar()
Phoneno = tk.StringVar()
var = tk.IntVar()
age = tk.IntVar()

# Set background image
image2 = Image.open('reg3.png')
image2 = image2.resize((1700, 800), Image.ANTIALIAS)
background_image = ImageTk.PhotoImage(image2)
background_label = tk.Label(window, image=background_image)
background_label.image = background_image
background_label.place(x=0, y=0)

# Database connection
db = sqlite3.connect('evaluation.db')
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS registration(
        Fullname TEXT, 
        address TEXT, 
        userid TEXT, 
        Email TEXT, 
        Phoneno TEXT, 
        Gender TEXT, 
        age TEXT, 
        College TEXT,
        face BLOB
    )
""")
db.commit()

# Function to insert data
def insert():
    fname = Fullname.get()
    addr = address.get()
    College = college_name.get()
    un = userid.get()
    email = Email.get()
    mobile = Phoneno.get()
    gender = var.get()
    age_val = age.get()
    face_path = f"faces/{un}.jpg"  # Path for the face image

    with sqlite3.connect('evaluation.db') as db:
        c = db.cursor()

    # Find existing user ID
    find_user = ('SELECT * FROM registration WHERE userid = ?')
    c.execute(find_user, [(un)])

    # Email validation
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        email_valid = True
    else:
        email_valid = False

    # Validation checks
    if fname.isdigit() or fname == "":
        ms.showinfo("Message", "Please enter a valid name")
    elif addr == "":
        ms.showinfo("Message", "Please enter address")
    elif email == "" or not email_valid:
        ms.showinfo("Message", "Please enter a valid email")
    elif len(mobile) != 10 or not mobile.isdigit():
        ms.showinfo("Message", "Please enter a 10-digit mobile number")
    elif age_val > 100 or age_val <= 0:
        ms.showinfo("Message", "Please enter a valid age")
    elif not os.path.exists(face_path):
        ms.showinfo("Message", "Please capture your face image first")
    elif c.fetchall():
        ms.showerror('Error!', 'User ID already taken. Try a different one.')
    else:
        conn = sqlite3.connect('evaluation.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO registration(Fullname, address, userid, Email, Phoneno, Gender, age, College, face) VALUES(?,?,?,?,?,?,?,?,?)',
                (fname, addr, un, email, mobile, gender, age_val, College, face_path))
            conn.commit()
            ms.showinfo('Success!', 'Account Created Successfully!')
            call_login_file()  # Call the login file after successful registration

# Define variables
face_captured = False  # Flag to check if face has been captured

# Function to capture the student's face
def capture_face():
    global face_captured
    un = userid.get()
    if un == 0:
        ms.showinfo("Message", "Please enter User ID first")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    ms.showinfo("Message", "Look at the camera and press 'q' to capture your face")
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Capture Face", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to capture
            if len(faces) > 0:
                face_path = f"faces/{un}.jpg"
                if not os.path.exists("faces"):
                    os.makedirs("faces")
                cv2.imwrite(face_path, frame)
                ms.showinfo("Success!", f"Face image captured and saved as {face_path}")
                face_captured = True  # Set flag to True after successful capture
            else:
                ms.showinfo("Error!", "No face detected. Try again.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to insert data and call login file if conditions are met
def insert():
    global face_captured
    fname = Fullname.get()
    addr = address.get()
    College = college_name.get()
    un = userid.get()
    email = Email.get()
    mobile = Phoneno.get()
    gender = var.get()
    age_val = age.get()
    face_path = f"faces/{un}.jpg"  # Path for the face image

    with sqlite3.connect('evaluation.db') as db:
        c = db.cursor()

    # Find existing user ID
    find_user = ('SELECT * FROM registration WHERE userid = ?')
    c.execute(find_user, [(un)])

    # Email validation
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if re.search(regex, email):
        email_valid = True
    else:
        email_valid = False

    # Validation checks
    if fname.isdigit() or fname == "":
        ms.showinfo("Message", "Please enter a valid name")
    elif addr == "":
        ms.showinfo("Message", "Please enter address")
    elif email == "" or not email_valid:
        ms.showinfo("Message", "Please enter a valid email")
    elif len(mobile) != 10 or not mobile.isdigit():
        ms.showinfo("Message", "Please enter a 10-digit mobile number")
    elif age_val > 100 or age_val <= 0:
        ms.showinfo("Message", "Please enter a valid age")
    elif not face_captured:
        ms.showinfo("Message", "Please capture your face image first")
    elif c.fetchall():
        ms.showerror('Error!', 'User ID already taken. Try a different one.')
    else:
        conn = sqlite3.connect('evaluation.db')
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO registration(Fullname, address, userid, Email, Phoneno, Gender, age, College, face) VALUES(?,?,?,?,?,?,?,?,?)',
                (fname, addr, un, email, mobile, gender, age_val, College, face_path))
            conn.commit()
            ms.showinfo('Success!', 'Account Created Successfully!')
            call_login_file()  # Call the login file after successful registration
            face_captured = False  # Reset the flag for the next user

# Function to call the login file
def call_login_file():
    try:
        subprocess.run(["python", "login.py"])  # Replace 'login.py' with the correct login script
    except FileNotFoundError:
        ms.showerror("Error", "The login file could not be found!")
    except Exception as e:
        ms.showerror("Error", f"An error occurred: {e}")


# UI Components
l1 = tk.Label(window, text="Registration Form", font=("Times new roman", 30, "bold"), bg="#86c6f0", fg="white")
l1.place(x=410, y=50)

# Full Name
l2 = tk.Label(window, text="Full Name :", width=14, font=("Times new roman", 15), bg="#227c90", fg="white")
l2.place(x=165, y=150)
t1 = tk.Entry(window, textvar=Fullname, width=35, font=('', 15))
t1.place(x=450, y=150)

# Address
l3 = tk.Label(window, text="Address :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l3.place(x=165, y=200)
t2 = tk.Entry(window, textvar=address, width=35, font=('', 15))
t2.place(x=450, y=200)

# College Name
l4 = tk.Label(window, text="College Name :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l4.place(x=165, y=250)
t3 = tk.Entry(window, textvar=college_name, width=35, font=('', 15))
t3.place(x=450, y=250)

# Email
l5 = tk.Label(window, text="E-mail :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l5.place(x=165, y=300)
t4 = tk.Entry(window, textvar=Email, width=35, font=('', 15))
t4.place(x=450, y=300)

# Phone Number
l6 = tk.Label(window, text="Phone Number :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l6.place(x=165, y=350)
t5 = tk.Entry(window, textvar=Phoneno, width=35, font=('', 15))
t5.place(x=450, y=350)

# Gender
l7 = tk.Label(window, text="Gender :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l7.place(x=165, y=400)
tk.Radiobutton(window, text="Male", padx=5, width=10, bg="#EAFAF1", font=("bold", 15), variable=var, value=1).place(x=450, y=400)
tk.Radiobutton(window, text="Female", padx=20, width=12, bg="#EAFAF1", font=("bold", 15), variable=var, value=2).place(x=650, y=400)

# Age
l8 = tk.Label(window, text="Age :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l8.place(x=165, y=450)
t6 = tk.Entry(window, textvar=age, width=35, font=('', 15))
t6.place(x=450, y=450)

# User ID
l9 = tk.Label(window, text="User ID :", width=14, font=("Times new roman", 15, "bold"), bg="#227c90", fg="white")
l9.place(x=165, y=500)
t7 = tk.Entry(window, textvar=userid, width=35, font=('', 15))
t7.place(x=450, y=500)

# Submit Button
btn = tk.Button(window, text="SUBMIT", bg="#eb6683", font=("", 15), fg="black", width=10, height=1, command=insert)
btn.place(x=450, y=600)

# Capture Face Button
btn_face = tk.Button(window, text="CAPTURE FACE", bg="#eb6683", font=("", 15), fg="black", width=15, height=1, command=capture_face)
btn_face.place(x=670, y=600)

# Run the application
window.mainloop()
