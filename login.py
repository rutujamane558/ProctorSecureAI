import tkinter as tk
from tkinter import messagebox as ms
import sqlite3
import cv2
from subprocess import call
from PIL import Image, ImageTk
import os

# Initialize the root window
root = tk.Tk()
root.configure(background="black")
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("Login Form")

# Background Image
image2 = Image.open('11.png')
image2 = image2.resize((w, h), Image.ANTIALIAS)
background_image = ImageTk.PhotoImage(image2)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0)

# Marquee Text
def shift():
    x1, y1, x2, y2 = canvas.bbox("marquee")
    if x2 < 0 or y1 < 0:  # Reset the coordinates
        x1 = canvas.winfo_width()
        y1 = canvas.winfo_height() // 2
        canvas.coords("marquee", x1, y1)
    else:
        canvas.move("marquee", -2, 0)
    canvas.after(1000 // fps, shift)

canvas = tk.Canvas(root, bg="#5499C7")
canvas.pack()
text_var = "Login Face Authentication"
canvas.create_text(0, -2000, text=text_var, font=('Algerian', 25, 'bold'), fill='black', tags=("marquee",), anchor='w')
canvas['width'], canvas['height'], fps = 1600, 100, 40
shift()

# Database connection
db = sqlite3.connect('evaluation.db')
cursor = db.cursor()

# Create the user table if it doesn't exist
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

# Function for Face Authentication
def Test_database():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainingdata.yml')  # Load trained data
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Mapping IDs to class/student names (example data)
    student_data = {1: "Student A - Class 10", 2: "Student B - Class 12"}

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # Width
    cam.set(4, 480)  # Height

    font = cv2.FONT_HERSHEY_SIMPLEX
    minW, minH = 0.1 * cam.get(3), 0.1 * cam.get(4)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 8, minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 50:  # Successful Authentication
                name = student_data.get(id, f"known ID: {id}")  # Fetch student/class name
                confidence_text = f"{100 - int(confidence)}%"
                cv2.putText(img, name, (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, confidence_text, (x + 5, y + h - 5), font, 1, (0, 255, 0), 1)
                cv2.putText(img, "Face Authentication Successful!", (40, 40), font, 1, (0, 255, 0), 2)
                cv2.imshow('Camera', img)
                cam.release()
                cv2.destroyAllWindows()

                ms.showinfo("Success", f"Welcome {name}!")
                call(['python', 'GUI_Master.py'])  # Call the next GUI
                return

            else:  # Unsuccessful Authentication
                cv2.putText(img, "unknown", (x + 5, y - 5), font, 1, (0, 0, 255), 2)
                cv2.putText(img, "Authentication Failed", (40, 40), font, 1, (0, 0, 255), 2)

        cv2.imshow('Camera', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cam.release()
    cv2.destroyAllWindows()
    ms.showerror("Error", "Authentication failed. Try again!")

# Exit Function
def window():
    root.destroy()

# Buttons
btn_capture = tk.Button(root, text="Face Authentication", bg="#A9CCE3", font=('times', 15, ' bold '), fg="black",bd=20, width=15, height=1, command=Test_database)
btn_capture.place(x=40, y=150)

btn_exit = tk.Button(root, text="Exit", command=window, width=15, height=1,bd=20,font=('times', 15, ' bold '), bg="#eb6683", fg="black")
btn_exit.place(x=40, y=250)

root.mainloop()
