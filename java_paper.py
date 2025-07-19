import tkinter as tk
from tkinter import messagebox as mb
import pygame  # For playing alert sound
import cv2     # For camera-based cheating detection
from PIL import Image, ImageTk
import threading
import speech_recognition as sr

# Initialize cheating detection
pygame.init()
pygame.mixer.init()

# Global Variables
question_number = 0
score = 0
window = None
stop_threads = False
warnings_given = 0
question_time = 20  # 20 seconds per question
total_exam_time = 900  # 15 minutes (900 seconds)
time_remaining = total_exam_time

# Questions, Options, and Answers (C++ questions)
quiz_data = [
    {"question": "What is the default value of an int variable in Java?", "options": ["0", "null", "undefined", "1"], "answer": "0"},
    {"question": "Which of the following is used to declare a constant in Java?", "options": ["const", "constant", "final", "static"], "answer": "final"},
    {"question": "What is the size of a float in Java?", "options": ["32 bits", "64 bits", "16 bits", "8 bits"], "answer": "32 bits"},
    {"question": "Which of these is a valid way to create a thread in Java?", "options": ["Thread t = new Thread(); t.start();", "Thread t = new Thread(); t.run();", "Thread.start();", "None of the above"], "answer": "Thread t = new Thread(); t.start();"},
    {"question": "Which of these methods is used to start a thread in Java?", "options": ["run()", "start()", "begin()", "init()"], "answer": "start()"},
    {"question": "Which of the following is used for input in Java?", "options": ["Scanner", "BufferedReader", "System.in", "All of the above"], "answer": "All of the above"},
    {"question": "Which of the following is the correct way to define a method in Java?", "options": ["void method_name()", "method_name void()", "public void method_name()", "method_name public void()"], "answer": "public void method_name()"},
    {"question": "Which of these is not a valid data type in Java?", "options": ["int", "double", "string", "boolean"], "answer": "string"},
    {"question": "Which of the following is the base class for all exceptions in Java?", "options": ["Exception", "Throwable", "Error", "RuntimeException"], "answer": "Throwable"},
    {"question": "Which of these is not an access modifier in Java?", "options": ["public", "private", "protected", "secure"], "answer": "secure"}
]


# Function to handle warnings
def handle_warning():
    global warnings_given, window
    warnings_given += 1
    if warnings_given <= 3:
        mb.showwarning("Warning", f"Speech detected! This is warning {warnings_given} of 3.")
    if warnings_given == 3:
        cheating_detected()

# Function for cheating detection
def cheating_detected():
    pygame.mixer.music.load("popup_alert.wav")  # Load alert audio
    pygame.mixer.music.play()             # Play alert sound
    mb.showwarning("Cheating Detected", "You have exceeded the allowed warnings. Please refrain from cheating.")

# Function to monitor faces
def start_face_detection():
    cap = cv2.VideoCapture(0)  # Open webcam
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while not stop_threads:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) != 1:  # If no face or multiple faces detected
            pygame.mixer.music.load("popup_alert.wav")  # Trigger an alert sound
            pygame.mixer.music.play()
            mb.showwarning("Warning", "Cheating Detected: no face detected.")

        # Display camera frame on Tkinter canvas
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((400, 300), Image.ANTIALIAS)  # Resize the frame to fit the canvas
        img_tk = ImageTk.PhotoImage(img)

        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()

# Function to monitor speech
def start_speech_detection():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)

    while not stop_threads:
        try:
            with mic as source:
                print("Listening for speech...")
                audio_data = recognizer.listen(source, timeout=5)  # Listen for speech (with a timeout)

                # Save the detected audio to a file without any alerts
                save_audio_to_file(audio_data)

        except sr.WaitTimeoutError:
            # No speech detected within the timeout period, continue monitoring
            continue

        except Exception as e:
            print(f"Error in speech detection: {e}")

# Function to save audio to a WAV file
def save_audio_to_file(audio_data):
    # Set the file name and path
    file_path = "detected_audio.wav"

    # Save the audio data to a file
    with open(file_path, "wb") as f:
        f.write(audio_data.get_wav_data())  # Save as WAV format
    print(f"Audio saved to {file_path}")

# Function to display next question
def next_question():
    global question_number, score
    selected_option = option_var.get()

    # Ensure valid option selected
    if selected_option is None:
        mb.showwarning("No Selection", "Please select an option before proceeding.")
        return

    if selected_option == quiz_data[question_number]['answer']:
        score += 1  # Increase score if answer is correct

    question_number += 1

    if question_number < len(quiz_data):
        display_question()
    else:
        mb.showinfo("Quiz Completed", f"Your final score is: {score}/{len(quiz_data)}")
        global stop_threads
        stop_threads = True
        window.destroy()

# Function to display previous question
def previous_question():
    global question_number
    if question_number > 0:
        question_number -= 1
        display_question()

# Function to display a question
def display_question():
    global lbl_question, radio_buttons, option_var, question_number
    option_var.set(None)  # Reset radio button selection

    # Check if the question_number is within bounds
    if question_number < len(quiz_data):
        question_data = quiz_data[question_number]
        lbl_question.config(text=f"Q{question_number + 1}: {question_data['question']}")

        for i, option in enumerate(question_data['options']):
            radio_buttons[i].config(text=option, value=option)
    else:
        mb.showinfo("Quiz Completed", f"Your final score is: {score}/{len(quiz_data)}")
        global stop_threads
        stop_threads = True
        window.destroy()
        
# Modify the submit button to show the success message when the exam is submitted
def submit_exam():
    mb.showinfo("Exam Submitted", "Exam Submitted Successfully. Thank you!")
    global stop_threads
    stop_threads = True
    window.destroy()

# Main Program
if __name__ == "__main__":
    # Initialize main window
    window = tk.Tk()
    window.title("C++ Examination System")
    window.geometry("800x600")  # Increased window size
    window.configure(bg="#90d5ff")

    # Create Canvas for Camera Feed
    canvas = tk.Canvas(window, width=400, height=300)
    canvas.grid(row=0, column=0, columnspan=4, pady=10)  # Camera at the top, spanning all columns

    # Welcome message
    lblrules = tk.Label(window,
                        text="This quiz contains 10 questions\nYou will get 20 seconds to solve a question\nOnce you select an option, it will be final.\nYou are allowed 3 warnings for speech detection.",
                        width=80,
                        font=("Times", 14),
                        background="#90d5ff",
                        foreground="black")
    lblrules.grid(row=1, column=0, columnspan=4, pady=10)

    # Question label
    lbl_question = tk.Label(window, text="", font=("Times", 16), background="#90d5ff", foreground="black")
    lbl_question.grid(row=2, column=0, columnspan=4, pady=10)

    # Options (Radio Buttons)
    option_var = tk.StringVar(value=None)
    radio_buttons = []
    for i in range(4):  # 4 options per question
        rb = tk.Radiobutton(window, text="", variable=option_var, value=None, font=("Times", 14), background="#90d5ff", foreground="black", selectcolor="white")
        rb.grid(row=3 + i, column=0, columnspan=4, sticky="w", padx=20, pady=5)
        radio_buttons.append(rb)

    # Buttons (Next, Previous, Submit)
    btn_previous = tk.Button(window, text="Previous", command=previous_question, font=("Times", 14), bg="#90d5ff", fg="black", width=12)
    btn_previous.grid(row=8, column=0, pady=10)

    btn_next = tk.Button(window, text="Next", command=next_question, font=("Times", 14), bg="#90d5ff", fg="black", width=12)
    btn_next.grid(row=8, column=1, pady=10)

    # Modify the Submit Exam button command
    btn_submit = tk.Button(window, text="Submit Exam", command=submit_exam, font=("Times", 14), bg="#eb6683", fg="black", width=12)
    btn_submit.grid(row=8, column=2, pady=10)

    # Display the first question
    display_question()

    # Start face detection in a separate thread
    face_thread = threading.Thread(target=start_face_detection, daemon=True)
    face_thread.start()

    # Start speech detection in a separate thread
    speech_thread = threading.Thread(target=start_speech_detection, daemon=True)
    speech_thread.start()

    # Start the main loop
    window.mainloop()
