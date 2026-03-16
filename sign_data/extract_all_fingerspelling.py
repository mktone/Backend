"""
raw_sign/ 안의 영상 31개를 순서대로 자모에 매핑하여
MediaPipe Holistic keypoint 추출 + npy 저장 + mapping_fingerspelling.json 생성

사용법:
    python3 sign_data/extract_all_fingerspelling.py

출력:
    sign_data/fingerspelling_db/{자모}_keypoints.npy  (shape: frames, 543, 3)
    sign_data/mapping_fingerspelling.json
"""

import os
import json
import cv2
import numpy as np
import mediapipe as mp

# 자모 순서 (영상 번호 오름차순)
JAMO_ORDER = [
    "ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅊ",
    "ㅋ", "ㅌ", "ㅍ", "ㅎ", "ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ",
    "ㅜ", "ㅠ", "ㅡ", "ㅣ", "ㅐ", "ㅒ", "ㅔ", "ㅖ", "ㅚ", "ㅟ", "ㅢ",
]

BASE_DIR   = os.path.dirname(__file__)
RAW_DIR    = os.path.join(BASE_DIR, "raw_sign")
OUTPUT_DIR = os.path.join(BASE_DIR, "fingerspelling_db")
OUTPUT_MAP = os.path.join(BASE_DIR, "mapping_fingerspelling.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

mp_holistic = mp.solutions.holistic
mp_drawing  = mp.solutions.drawing_utils


def extract_video(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS)
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    all_keypoints = []

    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = holistic.process(rgb)

            def lm_to_np(landmarks, n):
                if landmarks:
                    return np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark], dtype=np.float32)
                return np.zeros((n, 3), dtype=np.float32)

            pose  = lm_to_np(result.pose_landmarks,       33)
            face  = lm_to_np(result.face_landmarks,      468)
            lhand = lm_to_np(result.left_hand_landmarks,  21)
            rhand = lm_to_np(result.right_hand_landmarks, 21)

            all_keypoints.append(np.concatenate([pose, face, lhand, rhand], axis=0))

    cap.release()

    seq = np.array(all_keypoints)  # (frames, 543, 3)
    actual_frames = len(seq)
    duration_sec  = actual_frames / fps if fps > 0 else 0.0

    return seq, actual_frames, fps, duration_sec


def main():
    video_files = sorted([
        f for f in os.listdir(RAW_DIR)
        if f.upper().endswith((".MOV", ".MP4", ".AVI"))
        and "mediapipe" not in f.lower()
    ])

    if len(video_files) != len(JAMO_ORDER):
        print(f"[WARNING] 영상 {len(video_files)}개 vs 자모 {len(JAMO_ORDER)}개 — 개수 불일치")

    mapping = []

    for i, (filename, jamo) in enumerate(zip(video_files, JAMO_ORDER)):
        video_path = os.path.join(RAW_DIR, filename)
        npy_abs    = os.path.join(OUTPUT_DIR, f"{jamo}_keypoints.npy")
        npy_path   = os.path.join("sign_data", "fingerspelling_db", f"{jamo}_keypoints.npy")

        print(f"[{i+1}/{len(video_files)}] {jamo}  ←  {filename}")

        seq, frames, fps, duration_sec = extract_video(video_path)
        np.save(npy_abs, seq)

        mapping.append({
            "jamo":         jamo,
            "duration_sec": round(duration_sec, 4),
            "frames":       frames,
            "fps":          round(fps, 4),
            "npy_path":     npy_path,
        })
        print(f"     저장: {npy_path}  shape: {seq.shape}")

    with open(OUTPUT_MAP, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n완료: {OUTPUT_MAP}")


if __name__ == "__main__":
    main()
