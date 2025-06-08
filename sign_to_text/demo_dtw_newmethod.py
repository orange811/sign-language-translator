import collections
import numpy as np
import cv2
import time
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw  # Make sure you have installed fastdtw
import pickle
from sklearn.preprocessing import MinMaxScaler

import warnings
warnings.filterwarnings('ignore')

model_asset_path="data/pose_landmarker.task"
dtw_templates_path = "data/dtw_templates_best_of_all.pkl"

# Load DTW templates
with open(dtw_templates_path, "rb") as f:
    dtw_templates = pickle.load(f)  # Format: {"label1": [seq1, seq2, ...], ...}

# Initialize video capture
video = cv2.VideoCapture(0)
time.sleep(2.0)

landmark_buffer = collections.deque(maxlen=45)
last_prediction = "Waiting..."
last_confidence = 0.0
frame_counter = 0
frame_ctr_display = 0

# Drawing function
def draw_landmarks_on_image(rgb_image, pose_detection_result):
    annotated_image = np.copy(rgb_image)
    if pose_detection_result.pose_landmarks:
        for pose_landmarks in pose_detection_result.pose_landmarks:
            proto = landmark_pb2.NormalizedLandmarkList()
            proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=l.x, y=l.y, z=l.z)
                for l in pose_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
                annotated_image, proto,
                solutions.pose.POSE_CONNECTIONS,
                solutions.drawing_styles.get_default_pose_landmarks_style(),
            )
    return annotated_image

pointsList = [0,7,8,11,12,13,14,15,16,17,18,19,20,21,22]

# Pose detector
pose_options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path = model_asset_path)
)
pose_detector = vision.PoseLandmarker.create_from_options(pose_options)

# DTW comparison function
# def dtw_predict(sequence, templates_dict):
#     min_dist = float("inf")
#     best_label = "Unknown"
#     for label, template_list in templates_dict.items():
#         for template in template_list:
#             dist, _ = fastdtw(sequence, template, dist=euclidean)
#             if dist < min_dist:
#                 min_dist = dist
#                 best_label = label
#     print(f"Min DTW distance: {min_dist} for label: {best_label}")

#     #if min_dist < 4.3:  # Chosen after experimentation
#     return best_label
#     return "Unknown"
    
def dtw_predict(sequence, templates_dict):
    best_label = "Unknown"
    min_avg_dist = float("inf")

    for label, template_list in templates_dict.items():
        total_dist = 0.0
        num_sequences = len(template_list)

        for template in template_list:
            dist, _ = fastdtw(sequence, template, dist=euclidean)
            total_dist += dist

        avg_dist = total_dist / num_sequences

        print(f"Avg DTW distance: {avg_dist:.4f} for label: {label}")

        if avg_dist < min_avg_dist:
            min_avg_dist = avg_dist
            best_label = label

    print(f"Min avg DTW distance: {min_avg_dist:.4f} for label: {best_label}")
    # Convert distance to pseudo-confidence (scaled and clipped)
    confidence = min(100, max(0,(120-min_avg_dist)*10))  # adjust as needed
    if min_avg_dist < 130:
        return best_label, confidence
    return "Unknown", 0
    
frame_ctr_display = 0    
recording = False  # Set to True if you want to record the video

# Main loop
while True:
    ret, frame = video.read()
    if not ret:
        break

    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
    pose_result = pose_detector.detect(mp_image)

    annotated = draw_landmarks_on_image(rgb_image, pose_result)
    frame = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
    
    if pose_result.pose_landmarks:
        frame = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
        if recording:
            frame_ctr_display = frame_counter  # New: show count from 0 to 45
            frame_counter += 1

            for landmarks in pose_result.pose_landmarks:
                pose_data = [
                    [landmarks[i].x, landmarks[i].y, landmarks[i].z]#, landmarks[i].visibility]
                    for i in pointsList
                ]
                landmark_buffer.append(np.array(pose_data).flatten())

            # if len(landmark_buffer) == 45 and frame_counter > 45:
            if frame_counter == 45:
                sequence = np.array(landmark_buffer)

                # #scaling to fit demo data
                scaler = MinMaxScaler()
                sequence = scaler.fit_transform(sequence)

                # predicted_label = dtw_predict(sequence, dtw_templates)
                # last_prediction = predicted_label
                predicted_label, confidence = dtw_predict(sequence, dtw_templates)
                last_prediction = predicted_label
                last_confidence = confidence

                # Reset after prediction
                frame_counter = 0
                frame_ctr_display = 0
                recording = False

        # cv2.putText(frame, f"Predicted: {last_prediction}", (10, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # cv2.putText(frame, f"{frame_ctr_display}", (10, 100),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # === Draw translucent box ===
        overlay = frame.copy()
        box_top_left = (10, 10)
        box_bottom_right = (400, 80)
        cv2.rectangle(overlay, box_top_left, box_bottom_right, (0, 0, 0), -1)  # Black box

        # Blend with original image (translucent effect)
        alpha = 0.5  # Transparency factor
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

        # === Add only the final word after dot or underscore inside box ===
        simple_label = last_prediction.split('.')[-1].split('_')[-1].strip()
        text = f"Prediction: {simple_label}"
        accuracy_text = f"Confidence: {last_confidence:.1f}%"  

        # OLD
        # text = f"Prediction: {last_prediction}"        

        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(frame, accuracy_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(frame, f"{frame_ctr_display}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Old auto-recording logic (commented out)
        # frame_counter += 1
        # frame_ctr_display = (frame_ctr_display + 1) % 46

    cv2.imshow("Pose Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("r") and not recording:
        for i in range(2, 0, -1):
            temp_frame = frame.copy()
            cv2.putText(temp_frame, f"Recording in {i}...", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
            cv2.imshow("Pose Detection", temp_frame)
            cv2.waitKey(1000)  # wait 1 second per countdown step
        recording = True
        landmark_buffer.clear()
        frame_counter = 0
        frame_ctr_display = 0

video.release()
cv2.destroyAllWindows()
