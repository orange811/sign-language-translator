# Bidirectional Indian Sign Language Translator (Word-Level)

This repository implements a bidirectional Indian Sign Language (ISL) translation prototype developed as a final-year engineering project. The system supports (i) **ISL → Text** through vision-based gesture recognition and (ii) **Text → ISL** through **gloss generation** (word-level sign representations) followed by dictionary-driven sign video retrieval and merging.

## Motivation & Research Background

Sign languages are visual languages that use coordinated hand gestures, body movement, and facial expressions. In spoken-language environments, Deaf and Hard-of-Hearing communities often face communication barriers that can be reduced with assistive translation tools.

This project is motivated by and guided by the following Springer publication (survey + background on landmark-based pipelines and temporal modeling):

- Piyush Jain, Neha Pattanshetti, Esha Hundekar, Mousami Turuk, Sakshi Hosamani, “Advances in Machine Learning Techniques for Sign Language Interpretation,” *Intelligent Strategies for ICT*, Springer Nature Singapore, 2025.  
  DOI: https://doi.org/10.1007/978-981-96-5604-2_32

## Dataset

For sign video samples and experiments, we used the **INCLUDE dataset by AI4Bharat**:
- GitHub: https://github.com/AI4Bharat/INCLUDE
- Hugging Face: https://huggingface.co/datasets/ai4bharat/INCLUDE

## System Architecture

### UI workflow

![UI workflow](/assets/ui-workflow.png)

### 1) ISL → Text (gesture recognition)

Pipeline (high level):
1. Capture a sign video (or camera stream).
2. Extract pose/landmark features using **MediaPipe**.
3. Model temporal motion:
   - **LSTM** was implemented first to explore scaling to a larger vocabulary.
   - **Dynamic Time Warping (DTW)** was added later and used for the real-time demo.

Workflow (sign-to-text):

![Sign-to-text workflow](/assets/stt-workflow.png)

Main demo script used by the UI:
- `sign_to_text/demo_dtw_newmethod.py`

Preprocessing utilities used to build landmark sequences:
- `sign_to_text/preprocessing/preprocessStuff_step1.py` (landmarks → CSV)
- `sign_to_text/preprocessing/findImpFrames_step2.py` (select an “eventful” frame window)
- `sign_to_text/preprocessing/dtw_sequence_generator.ipynb` (sequence prep / experimentation)

### 2) Text → ISL (gloss + video retrieval)

Pipeline (high level):
1. Accept text input (typed; speech-to-text support exists in the repo).
2. Convert text into an ISL-oriented gloss sequence (word-level sign tokens).
3. Map gloss tokens to available dictionary entries (including synonym mapping where required).
4. Retrieve sign videos and merge them into a single output video.

Workflow (text-to-sign):

![Text-to-sign workflow](/assets/tts_workflow.png)

Core modules:
- `text_to_sign/text_to_isl_gloss.py`
- `text_to_sign/synonym_matcher.py`
- `text_to_sign/generate_video.py`
- `text_to_sign/speech_to_text.py`

### UI

A Tkinter-based interface ties both directions together:
- `txt_signUI.py`

## Results (Prototype Summary)

- **DTW** reached ~**94% accuracy** on an **11-gesture subset** used during experimentation.
- **LSTM** was initially explored for scaling to **263 gestures** (prototype accuracy ~**50%** in our setup).
- Performance is primarily governed by training data availability/coverage as vocabulary size increases.

## UI (Screenshots)

Sign-to-text demo (DTW prediction + confidence overlay):

![DTW predictions](/assets/predictions.png)

Text-to-sign UI showing text → gloss conversion, dictionary mapping, and merged video playback:

![Text-to-sign UI](/assets/tts_ui.png)
(Video in screenshot is from the aforementioned INCLUDE dataset)
## Citation

```bibtex
@InProceedings{10.1007/978-981-96-5604-2_32,
author="Jain, Piyush
and Pattanshetti, Neha
and Hundekar, Esha
and Turuk, Mousami
and Hosamani, Sakshi",
editor="Kaiser, M. Shamim
and Xie, Juanying
and Rathore, Vijay Singh",
title="Advances in Machine Learning Techniques for Sign Language Interpretation",
booktitle="Intelligent Strategies for ICT",
year="2025",
publisher="Springer Nature Singapore",
address="Singapore",
pages="375--387",
abstract="Sign Language Recognition (SLR) has recently emerged as a crucial technology for facilitating communication between the hearing and deaf communities owing to the advancements in Machine Learning (ML). This paper surveys recent developments in SLR, focusing on widely appreciated and adopted techniques like Convolutional Neural Networks (CNNs), Transformers and Long Short-Term Memory (LSTM) networks. Frameworks such as MediaPipe detect hand, body, and facial landmarks with precision. Through comprehensive analysis and comparison of various approaches based on performance metrics including accuracy and Bilingual Evaluation Understudy (BLEU) scores, we identify the strengths of different architectures across static and dynamic gesture recognition techniques. Analysis reveals that MediaPipe-based frameworks combined with LSTM temporal modeling show promise in real-time applications. Building on previous performance and results, a real-time SLR system is presented that utilizes positional shifts in selected landmarks generated by MediaPipe to model gesture dynamics, alongside LSTM for temporal sequence modeling. The trained model then predicts gestures from live-fed video, ensuring efficient and accurate SLR.",
isbn="978-981-96-5604-2"
}
```
