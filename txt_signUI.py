import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
from PIL import Image, ImageTk
import subprocess
import cv2
import text_to_sign.generate_video as generate_video
from text_to_sign.speech_to_text import SpeechRecognizer
import text_to_sign.text_to_isl_gloss as stoi
from text_to_sign.synonym_matcher import map_gloss_sentence

# === CONFIGURATION ===
DTW_SIGN_TO_TEXT_PATH = "sign_to_text/demo_dtw_newmethod.py"
recognizer = SpeechRecognizer()
video_label = None  # global variable for video label in UI
cap = None  # global variable for video stream

# DTW Sign to Text Converter
def run_sign_to_text_converter():
    subprocess.Popen(["python", DTW_SIGN_TO_TEXT_PATH], shell=True)

def play_video(video_path):
    global cap
    cap = cv2.VideoCapture(video_path)
    show_frame()  # Start showing frames

def show_frame():
    global cap
    if cap is None:
        return

    ret, frame = cap.read()
    if not ret:
        cap.release()
        return

    # Get video_label size
    label_w = video_label.winfo_width()
    label_h = video_label.winfo_height()
    if label_w < 10 or label_h < 10:
        root.after(30, show_frame)
        return

    h, w = frame.shape[:2]
    aspect_ratio = w / h

    # Resize while maintaining aspect ratio
    if label_w / label_h > aspect_ratio:
        new_h = label_h
        new_w = int(aspect_ratio * new_h)
    else:
        new_w = label_w
        new_h = int(new_w / aspect_ratio)

    resized_frame = cv2.resize(frame, (new_w, new_h))
    frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)  # ✅ Fix color here
    img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))        # ✅ Use RGB version

    video_label.config(image=img)
    video_label.image = img
    root.after(30, show_frame)

def update_output_texts(gloss_sentence, dict_sentence):
    # Update gloss_text
    gloss_text.config(state='normal')
    gloss_text.delete(1.0, tk.END)
    gloss_text.insert(tk.END, gloss_sentence)
    gloss_text.config(state='disabled')
    # Update dict_text
    dict_text.config(state='normal')
    dict_text.delete(1.0, tk.END)
    dict_text.insert(tk.END, dict_sentence)
    dict_text.config(state='disabled')
    root.update_idletasks()
    
def on_generate(): 
    input_sentence = entry.get().strip()
    gloss_sentence = stoi.text_to_isl(input_sentence) 
    
    # ✅ Use NLP-based mapping
    word_to_path_mapping = map_gloss_sentence(gloss_sentence)
    dict_sentence = ""
    for word, mapping in word_to_path_mapping.items():
        if mapping:
            gloss_word = mapping.split(".")[-1].strip()
            dict_sentence += f"{word} → {gloss_word}\n"
    # dict_sentence = gloss_sentence #PLACEHOLDER: USE SYNONYM GENERATION LOGIC FUNCTION FROM SPEECH TO ISL
    update_output_texts(gloss_sentence, dict_sentence)
    if not input_sentence:
        messagebox.showerror("Error", "Please enter a sentence.")
        return
    result = generate_video.select_and_merge_videos(word_to_path_mapping)
    if result:
        play_video(result)
    else:
        messagebox.showinfo("Info", "No valid videos found for input.")

def on_mic_click():
    message_label.config(text="Please Wait...", fg="blue")
    root.update_idletasks()
    try:
        recognizer.setup_mic()
        message_label.config(text="Please Speak (max 10 sec)", fg="blue")
        root.update_idletasks()
        text = recognizer.listen()
        entry.delete(0, tk.END)
        entry.insert(0, text)
        message_label.config(text="Speech recognized.", fg="blue")
    except Exception as e:
        message_label.config(text=str(e), fg="red")

# === UI Setup ===
root = tk.Tk()
root.geometry("1000x700")  # wider window for two columns
root.resizable(True, True)
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=12)  

root.title("ISL Gloss to Video")

# === Two-column layout ===
main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True)

left_frame = tk.Frame(main_frame)
left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

right_frame = tk.Frame(main_frame, bg='black')
right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

# === Left Frame: Input + Buttons ===
tk.Label(left_frame, text="Enter a sentence or press the mic button to use speech to text:").pack(pady=10)

mic_img = tk.PhotoImage(file="img/mic_24.png")  # path to mic image file

frame = tk.Frame(left_frame)
frame.pack(pady=5, padx=10, fill='x')

mic_btn = tk.Button(frame, image=mic_img, command=on_mic_click)
mic_btn.image = mic_img
mic_btn.pack(side='left')

entry = tk.Entry(frame, width=50, font=default_font)
entry.pack(side='left', fill='x', expand=True)

message_label = tk.Label(left_frame, text="", fg="black")
message_label.pack(pady=(5, 10))

tk.Label(left_frame, text="Gloss Sentence:").pack(anchor='w', padx=10)
gloss_text = tk.Text(left_frame, height=3, width=50, state='disabled', bg='#f0f0f0')
gloss_text.pack(padx=10, pady=(0, 10))

tk.Label(left_frame, text="Dictionary Sentence:").pack(anchor='w', padx=10)
dict_text = tk.Text(left_frame, height=3, width=50, state='disabled', bg='#f0f0f0')
dict_text.pack(padx=10, pady=(0, 10))

btn_play = tk.Button(left_frame, text="Generate Sign & Play", command=on_generate)
btn_play.pack(pady=15)

btn_sign = tk.Button(left_frame, text="Sign To Text Converter", command=run_sign_to_text_converter)
btn_sign.pack(pady=25)

# === Right Frame: Video Display ===
video_label = tk.Label(right_frame, bg='black')
video_label.pack(fill='both', expand=True)

root.mainloop()
