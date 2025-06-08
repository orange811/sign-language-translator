import os

# Path to your dataset root
dataset_root = os.path.normpath("D:/Neha/BE/final year project/dataset include")

# Dictionary to store gloss mappings
gloss_dict = {}

# Walk through top-level category folders
for category in os.listdir(dataset_root):
    category_path = os.path.join(dataset_root, category)
    if os.path.isdir(category_path):
        # Walk through word folders inside each category
        for word_folder in os.listdir(category_path):
            word_path = os.path.join(category_path, word_folder)
            if os.path.isdir(word_path):
                # Extract gloss from folder name (assumes '1. Word' format)
                gloss = word_folder.split(". ", 1)[-1].lower()
                relative_path = os.path.join(category, word_folder).replace("\\", "/")
                gloss_dict[gloss] = relative_path

# Write dictionary to a .txt file
output_file = "gloss_dict.txt"
with open(output_file, "w") as f:
    f.write("{\n")
    for gloss, path in sorted(gloss_dict.items()):
        f.write(f'    "{gloss}": "{path}",\n')
    f.write("}\n")

print(f"GLOSS_DICT saved to {output_file}")
