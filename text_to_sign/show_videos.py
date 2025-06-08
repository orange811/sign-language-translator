import os
import ast
import random
import shutil
import cv2

DATASET_ROOT =  os.path.normpath("D:/Neha/BE/final year project/dataset include")  # Root folder of word videos
OUTPUT_FOLDER =  os.path.normpath("D:/Neha/BE/final year project/Text to sign/OutputSentenceVideos")
MERGED_VIDEO_PATH = os.path.join(OUTPUT_FOLDER, "merged_sentence_video.avi")
DICT_FILE = "data/gloss_dict.txt"

with open(DICT_FILE, "r") as f: 
    GLOSS_DICT = ast.literal_eval(f.read())

# === Utility to fix case/spaces mismatches ===
def find_folder_case_insensitive(root, relative_path):
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

    if not selected_videos:
        print("❌ No videos to merge.")
        return None

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

