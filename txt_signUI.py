import os
import shutil
import random
import cv2
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import ast
import subprocess

# === CONFIGURATION ===
sentence = "loud crowd"  # DEFAULT Input glossed sentence
DATASET_ROOT =  os.path.normpath("D:/Neha/BE/final year project/dataset include")  # Root folder of word videos
OUTPUT_FOLDER =  os.path.normpath("D:/Neha/BE/final year project/Text to sign/OutputSentenceVideos")
MERGED_VIDEO_PATH = os.path.join(OUTPUT_FOLDER, "merged_sentence_video.avi")
DTW_SIGN_TO_TEXT_PATH = os.path.normpath("sign_to_text/demo_dtw_newmethod.py")
DICT_FILE = "data/gloss_dict.txt"

with open(DICT_FILE, "r") as f:
    GLOSS_DICT = ast.literal_eval(f.read())
# Example use
# print(GLOSS_DICT["dog"])  # Outputs: Animals/1. Dog

# GLOSS_DICT = {
#     "loud": "Adjectives/1. loud",
#     "dog": "Animals/1. Dog",
#     "crowd": "People/83. Crowd",
#     "cow": "Animals/5. Cow",
#     # Add more as needed
# }
# === Ensure output folder exists ===
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# DTW Sign to Text Converter
def run_sign_to_text_converter():
    subprocess.Popen(["python", DTW_SIGN_TO_TEXT_PATH], shell=True)

# === Utility to fix case/spaces mismatches ===
def find_folder_case_insensitive(root, relative_path):
    """Safely resolve path even with slight mismatches in case or spacing."""
    current_path = root
    for part in os.path.normpath(relative_path).split(os.sep):
        try:
            matches = [name for name in os.listdir(current_path)
                       if name.lower().strip() == part.lower().strip()]
            if not matches:
                return None
            current_path = os.path.join(current_path, matches[0])
        except FileNotFoundError:
            return None
    return current_path

def create_output_folder():
    if os.path.exists(OUTPUT_FOLDER):
        shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)

def select_and_merge_videos(sentence):
    create_output_folder()
    selected_videos = []

    words = sentence.strip().lower().split()
    for idx, word in enumerate(words):
        if word not in GLOSS_DICT:
            print(f"❌ Word '{word}' not in gloss dictionary. Skipping.")
            continue

        # Resolve folder path safely
        folder_path = find_folder_case_insensitive(DATASET_ROOT, GLOSS_DICT[word])
        if not folder_path or not os.path.isdir(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            continue

        videos = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        if not videos:
            print(f"❌ No video in folder: {folder_path}")
            continue

         # Pick one video randomly
        selected_video = os.path.join(folder_path, random.choice(videos))
        selected_videos.append(selected_video)
        print(f"✅ Selected video for '{word}': {selected_video}")

        # chosen = random.choice(videos)
        # src = os.path.join(folder_path, chosen)
        # dst = os.path.join(OUTPUT_FOLDER, f"{idx+1}_{word}.avi")
        # shutil.copy2(src, dst)
        # selected_videos.append(dst)

    if not selected_videos:
        print("❌ No videos to merge.")
        return None
    # else:
    #     merged = None
    #     writer = None
    #     for video_path in selected_videos:
    #         cap = cv2.VideoCapture(video_path)
    #         if not cap.isOpened():
    #             print(f"❌ Could not open {video_path}")
    #             continue

    #         if writer is None:
    #             width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #             height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #             fps = int(cap.get(cv2.CAP_PROP_FPS)) or 24
    #             fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #             writer = cv2.VideoWriter(MERGED_VIDEO_PATH, fourcc, fps, (width, height))

    #         while True:
    #             ret, frame = cap.read()
    #             if not ret:
    #                 break
    #             writer.write(frame)
    #         cap.release()

    #     if writer:
    #         writer.release()
    #         print(f"✅ Merged video saved at: {MERGED_VIDEO_PATH}")


    # Get frame properties
    cap = cv2.VideoCapture(selected_videos[0])
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    cap.release()

    # Merge videos
    out = cv2.VideoWriter(MERGED_VIDEO_PATH, cv2.VideoWriter_fourcc(*'XVID'), fps, (w, h))
    for path in selected_videos:
        cap = cv2.VideoCapture(path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(cv2.resize(frame, (w, h)))
        cap.release()
    out.release()

    return MERGED_VIDEO_PATH

def play_video(video_path):
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

def on_generate():
    sentence = entry.get().strip()
    if not sentence:
        messagebox.showerror("Error", "Please enter a sentence.")
        return
    result = select_and_merge_videos(sentence)
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