import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import subprocess
import cv2
import text_to_sign.show_videos as show_videos

# === CONFIGURATION ===
sentence = "loud crowd"  # DEFAULT Input glossed sentence
DTW_SIGN_TO_TEXT_PATH = "sign_to_text/demo_dtw_newmethod.py"

# DTW Sign to Text Converter
def run_sign_to_text_converter():
    subprocess.Popen(["python", DTW_SIGN_TO_TEXT_PATH], shell=True)

def play_video(video_path): #keep in UI
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Resize frame to half scale
        frame = cv2.resize(frame, (int(frame.shape[1] / 2), int(frame.shape[0] / 2)))
        cv2.imshow("Merged Sign Video", frame)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

def on_generate(): #be in UI
    sentence = entry.get().strip()
    if not sentence:
        messagebox.showerror("Error", "Please enter a sentence.")
        return
    result = show_videos.select_and_merge_videos(sentence)
    if result:
        play_video(result)
    else:
        messagebox.showinfo("Info", "No valid videos found for input.")

# === UI Setup ===
root = tk.Tk()
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=12)  

root.title("ISL Gloss to Video")
tk.Label(root, text="Enter a sentence or press the mic button to use speech to text:").pack(pady=10)
mic_img = tk.PhotoImage(file="img/mic_24.png")  # path to mic image file

# frame with mic button and entry field
def on_mic_click():
    pass

frame = tk.Frame(root)
frame.pack(pady=5, padx=10, fill='x')

mic_btn = tk.Button(frame, image=mic_img, command=on_mic_click)
mic_btn.image = mic_img
mic_btn.pack(side='left')

entry = tk.Entry(frame, width=50, font  = default_font)
entry.pack(side='left', fill='x',expand=True)

# Message label
message_label = tk.Label(root, text="", fg="black")
message_label.pack(pady=(5, 10))

# Labels and text fields for Gloss and Dictionary sentences
tk.Label(root, text="Gloss Sentence:").pack(anchor='w', padx=10)
gloss_text = tk.Text(root, height=3, width=50, state='disabled', bg='#f0f0f0')
gloss_text.pack(padx=10, pady=(0, 10))

tk.Label(root, text="Dictionary Sentence:").pack(anchor='w', padx=10)
dict_text = tk.Text(root, height=3, width=50, state='disabled', bg='#f0f0f0')
dict_text.pack(padx=10, pady=(0, 10))

btn_play = tk.Button(root, text="Generate Sign & Play", command=on_generate)
btn_play.pack(pady=15)

btn_sign = tk.Button(root, text="Sign To Text Converter", command=run_sign_to_text_converter)
btn_sign.pack(pady=25)

root.mainloop()