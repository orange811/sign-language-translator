import os
import random
import shutil

# Define paths
# D:\Neha\BE\final year project\DTW_trial\data "D:\Neha\BE\final year project\dataset include\Seasons\61. Summer"
dataset_root = "D:\\Neha\\BE\\final year project\\dataset include"
output_root = "D:\\Neha\\BE\\final year project\\DTW_trial\\data\\sample videos per word class"

# Correct mapping from category to word folders
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
#     "Greetings": ["48. Hello", "55. Thank you"],
#     "Means_of_Transportation": ["16. train ticket"],
#     "Seasons": ["61. Summer"],
#     "Society": ["2. Death"]
# }

category_word_map = {
    "Adjectives": ["7. Deaf"],
    "Animals": ["4. Bird"],
    "Clothes": ["39. Suit", "40. Skirt"],
    "Means_of_Transportation": ["16. train ticket"],
    "People": ["66. Brother"],
    "Places": ["19. House", "23. Court", "28. Store or Shop"],
    "Seasons": ["64. Fall"],
    "Society": ["2. Death"]
}

# Create output root directory if it doesn't exist
os.makedirs(output_root, exist_ok=True)

for category, word_folders in category_word_map.items():
    category_path = os.path.join(dataset_root, category)
    
    for word_folder in word_folders:
        word_path = os.path.join(category_path, word_folder)
        if not os.path.isdir(word_path):
            print(f"Missing folder: {word_path}")
            continue

        # Get all .MOV files in the word folder
        video_files = [f for f in os.listdir(word_path) if f.lower().endswith(".mov")]

        if len(video_files) < 2:
            print(f"Not enough videos in {word_path}, found {len(video_files)}")
            sample_files = video_files  # Copy what exists
        else:
            sample_files = random.sample(video_files, 2)

        # Prepare output path
        # output_path = os.path.join(output_root, category, word_folder)
        output_path = os.path.join(output_root, word_folder)
        os.makedirs(output_path, exist_ok=True)

        # Copy selected files
        for file_name in sample_files:
            src = os.path.join(word_path, file_name)
            dst = os.path.join(output_path, file_name)
            shutil.copy(src, dst)
            print(f"Copied: {src} -> {dst}")

print("✅ Sampling complete.")
