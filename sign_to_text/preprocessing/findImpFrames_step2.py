import pandas as pd
import numpy as np
from tqdm import tqdm  # Import tqdm for progress bar

input_file = "D:\\Neha\\BE\\final year project\\DTW_trial\\data\\pose_landmarks_BEST_11.csv"
output_path = "D:\\Neha\\BE\\final year project\\DTW_trial\\data\\frame_range_BEST_11.csv"

# Function to calculate movement using Euclidean distance
def calculate_movement_euclidean(frame1, frame2):
    # Calculate the Euclidean distance between the corresponding points in the two frames (x, y, z)
    return np.sqrt(np.sum((frame1 - frame2) ** 2))


# Function to compute movements for all frames in a video
def compute_movements(frames):
    movements = []
    for i in range(1, len(frames)):
        movement = calculate_movement_euclidean(frames[i], frames[i - 1])
        movements.append(movement)
    return movements


# Function to apply exponential falloff weights
def apply_exponential_falloff(movement_scores, alpha=0.07):
    n = len(movement_scores)
    weights = np.exp(
        -alpha * np.abs(np.arange(n) - n / 2)
    )  # Exponential falloff centered on middle
    weighted_movements = movement_scores * weights
    return weighted_movements


# Function to select the best consecutive 45 frames based on movement
def select_consecutive_frames(movement_scores, window_size=45):
    max_sum = -1
    best_start = 0

    for i in range(len(movement_scores) - window_size + 1):
        current_sum = sum(movement_scores[i : i + window_size])
        if current_sum > max_sum:
            max_sum = current_sum
            best_start = i

    return best_start, best_start + window_size


# Load the CSV file
df = pd.read_csv(input_file)

# List to store results
results = []

# Group by 'class' and 'video_index' to process each video separately
grouped = df.groupby(["class", "video_index"])

print(f"Processed file {input_file}")

# Create tqdm progress bar for the number of videos to process
for (video_class, video_index), group in tqdm(
    grouped, desc="Processing Videos", total=len(grouped)
):
    # Extract only the x, y, z columns for points 0 to 24 (ignoring visibility)
    frames = group.filter(
        regex="(0|7|8|11|12|13|14|15|16|17|18|19|20|21|22)_(x|y)"
    ).values

    # Compute movement scores for the video
    movement_scores = compute_movements(frames)

    # Apply exponential falloff to movement scores
    weighted_movements = apply_exponential_falloff(np.array(movement_scores))

    # Select the best 45 consecutive frames
    start, end = select_consecutive_frames(weighted_movements)

    # Store the result
    results.append([video_class, video_index, start, end])

# Convert the results into a DataFrame
output_df = pd.DataFrame(results, columns=["class", "video_index", "start", "end"])

# Save to a new CSV file
output_df.to_csv(output_path, index=False)

print(f"Processing complete. Results saved as:\n{output_df}.")
