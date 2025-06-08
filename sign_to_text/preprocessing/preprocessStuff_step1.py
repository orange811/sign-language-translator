import os
import csv
import cv2
import mediapipe as mp
from tqdm import tqdm

'''Takes videos from the dataset and extracts pose landmarks into a csv from them using MediaPipe Pose.'''
# Define the paths
dataset_root_path =  "D:\\Neha\\BE\\final year project\\dataset include"  # Root folder for all classes
output_csv = "D:\\Neha\\BE\\final year project\\DTW_trial\\data\\pose_landmarks_BEST_10.csv"  # Output CSV file
# output_csv = "pose_landmarks_greetings_ALL.csv"  # if moving to datasets foledr above doesn't work

# Table: Mapping from Category to Words
# category_word_map = {
#     "Adjectives": ["7. Deaf"],
#     "Animals": ["1. Dog", "4. Bird"],
#     "Clothes": ["40. Skirt", "39. Suit", "44. Shoes"],
#     "Days_and_Time": ["86. Time", "67. Monday"],
#     "Greetings": ["48. Hello", "49. How are you", "55. Thank you", "54. Good night"],
#     "Home": ["40. Paint"],
#     "Means_of_Transportation": ["16. train ticket"],
#     "People": ["66. Brother"],
#     "Places": ["19. House", "23. Court", "28. Store or Shop"],
#     "Pronouns": ["41. you", "40. I"],
#     "Seasons": ["61. Summer", "64. Fall"],
#     "Society": ["2. Death"]
# }
# category_word_map = {
#     "Clothes": ["39. Suit"],
#     "Days_and_Time": ["67. Monday"],
#     "Animals": ["4. Bird"],
#     "Greetings": ["49. How are you", "55. Thank you", "48. Hello"],
#     "Seasons": ["61. Summer"],
#     "Society": ["2. Death"]
# }
category_word_map = {
    "Adjectives": ["7. Deaf"],
    "Animals": ["4. Bird"],
    "Clothes": ["39. Suit", "40. Skirt"],
    "Greetings": ["48. Hello"],
    "Means_of_Transportation": ["16. train ticket"],
    "People": ["66. Brother"],
    "Places": ["19. House", "23. Court", "28. Store or Shop"],
    "Seasons": ["64. Fall"],
    "Society": ["2. Death"]
}

# remove: shoes, summer
# add: train ticket, deaf,house

# Read already processed class names if CSV exists
processed_classes = set()   

if os.path.exists(output_csv):
    file_exists = True
    with open(output_csv, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed_classes.add(row["class"])

print(f"Already processed classes: {processed_classes}")

# Initialize MediaPipe Pose solution
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# Create or open CSV file for writing
with open(output_csv, mode="a", newline="") as file:
    writer = csv.writer(file)
    header = ["class", "video_index", "frame"] + [
        f"{part}_{axis}"
        for part in range(33)
        for axis in ["x", "y", "z", "visibility", "presence"]
    ]
    if not file_exists:
        writer.writerow(header)

    # class_folders = [
    #     f
    #     for f in os.listdir(dataset_root_path)
    #     if os.path.isdir(os.path.join(dataset_root_path, f))
    # ]

    # for class_folder in class_folders:
    #     # Clean the class name by stripping the numeric prefix and whitespace
    #     class_name = class_folder.split(".")[-1].strip().lower()

    #     class_path = os.path.join(dataset_root_path, class_folder)
    #     video_files = [f for f in os.listdir(class_path) if f.endswith(".MOV")]

    for category, words in category_word_map.items():
        for word in words:
            # SKIP ALREADY PROCESSED CLASSES
            class_key = f"{category}_{word}"
            if class_key in processed_classes:
                print(f"Skipping already processed: {class_key}")
                continue

            # ELSE PROCESS THE NEW CLASSES
            word_path = os.path.join(dataset_root_path, category, word)
            if not os.path.exists(word_path):
                print(f"Warning: Folder not found - {word_path}")
                continue
            
            video_files = [f for f in os.listdir(word_path) if f.endswith(".MOV")]
            for video_index, video_file in enumerate(video_files):
                video_path = os.path.join(word_path, video_file)
                print(f"Processing {video_path}")

                cap = cv2.VideoCapture(video_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                frame_count = 0


                with tqdm(
                    total=total_frames,
                    desc=f"Processing {category}/{word}/{video_file}",
                    unit="frame",
                ) as pbar:
                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break

                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        results = pose.process(rgb_frame)

                        if results.pose_landmarks:
                            landmarks = results.pose_landmarks.landmark
                            row = [f"{category}_{word}", video_index, frame_count]
                            # row = [class_name, video_index, frame_count]
                            for landmark in landmarks:
                                row.extend([landmark.x,landmark.y,landmark.z,
                                    landmark.visibility,landmark.presence,
                                ])
                            writer.writerow(row)

                        frame_count += 1
                        pbar.update(1)

                cap.release()

pose.close()
print(f"✅ Landmark data saved to {output_csv}")





# OLD PREPROCESSING CODE:

# import os
# import csv
# import cv2
# import mediapipe as mp
# from tqdm import tqdm

# '''Takes videos from the dataset and extracts pose landmarks into a csv from them using MediaPipe Pose.'''

# # Define the paths
# dataset_root_path =  "D:\\Neha\\BE\\final year project\\dataset include"  # Root folder for all classes
# output_csv = "datasets\\pose_landmarks_BEST.csv"  # Output CSV file
# # output_csv = "pose_landmarks_greetings_ALL.csv"  # if moving to datasets foledr above doesn't work

# # Initialize MediaPipe Pose solution
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(static_image_mode=False, model_complexity=2)

# # Create or open CSV file for writing
# with open(output_csv, mode="w", newline="") as file:
#     writer = csv.writer(file)
#     header = ["class", "video_index", "frame"] + [
#         f"{part}_{axis}"
#         for part in range(33)
#         for axis in ["x", "y", "z", "visibility", "presence"]
#     ]
#     writer.writerow(header)

#     class_folders = [
#         f
#         for f in os.listdir(dataset_root_path)
#         if os.path.isdir(os.path.join(dataset_root_path, f))
#     ]

#     for class_folder in class_folders:
#         # Clean the class name by stripping the numeric prefix and whitespace
#         class_name = class_folder.split(".")[-1].strip().lower()

#         class_path = os.path.join(dataset_root_path, class_folder)
#         video_files = [f for f in os.listdir(class_path) if f.endswith(".MOV")]

#         for video_index, video_file in enumerate(video_files):
#             video_path = os.path.join(class_path, video_file)
#             print(f"Processing {video_path}")

#             cap = cv2.VideoCapture(video_path)
#             total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#             frame_count = 0

#             with tqdm(
#                 total=total_frames,
#                 desc=f"Processing {video_file} ({class_name})",
#                 unit="frame",
#             ) as pbar:
#                 while cap.isOpened():
#                     ret, frame = cap.read()
#                     if not ret:
#                         break

#                     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                     results = pose.process(rgb_frame)

#                     if results.pose_landmarks:
#                         landmarks = results.pose_landmarks.landmark
#                         row = [class_name, video_index, frame_count]
#                         for landmark in landmarks:
#                             row.extend(
#                                 [
#                                     landmark.x,
#                                     landmark.y,
#                                     landmark.z,
#                                     landmark.visibility,
#                                     landmark.presence,
#                                 ]
#                             )
#                         writer.writerow(row)

#                     frame_count += 1
#                     pbar.update(1)

#             cap.release()

# pose.close()
# print(f"Landmark data saved to {output_csv}")