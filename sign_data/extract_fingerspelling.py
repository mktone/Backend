"""
영상에서 MediaPipe Holistic keypoint 추출 + 시각화 + 영상 저장
(body + face + left hand + right hand)

사용법:
    python3 sign_data/extract_fingerspelling.py sign_data/수어영상/IMG_2371.MOV

출력:
    sign_data/수어영상/IMG_2371_mediapipe.mp4  ← keypoint 오버레이 영상
    sign_data/수어영상/IMG_2371_keypoints.npy  ← shape: (frames, 543, 3)
                                                  pose 33 + face 468 + lhand 21 + rhand 21
"""

import sys
import os
import cv2
import numpy as np
import mediapipe as mp

VIDEO_PATH = sys.argv[1] if len(sys.argv) > 1 else "sign_data/수어영상/IMG_2371.MOV"

mp_holistic = mp.solutions.holistic
mp_drawing  = mp.solutions.drawing_utils
mp_styles   = mp.solutions.drawing_styles


def extract_and_save(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] 영상 열기 실패: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps          = cap.get(cv2.CAP_PROP_FPS)
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"영상: {os.path.basename(video_path)}")
    print(f"총 프레임: {total_frames}, FPS: {fps:.2f}, 해상도: {width}x{height}")

    base     = os.path.splitext(video_path)[0]
    out_path = base + "_mediapipe.mp4"
    fourcc   = cv2.VideoWriter_fourcc(*"mp4v")
    writer   = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    all_keypoints = []  # [(pose_33x3, face_468x3, lhand_21x3, rhand_21x3), ...]

    print("keypoint 추출 + 영상 저장 중...")
    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:
        idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = holistic.process(rgb)

            # --- keypoint 추출 ---
            def lm_to_np(landmarks, n):
                if landmarks:
                    return np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark], dtype=np.float32)
                return np.zeros((n, 3), dtype=np.float32)

            pose_kp  = lm_to_np(result.pose_landmarks,       33)
            face_kp  = lm_to_np(result.face_landmarks,      468)
            lhand_kp = lm_to_np(result.left_hand_landmarks,  21)
            rhand_kp = lm_to_np(result.right_hand_landmarks, 21)
            all_keypoints.append((pose_kp, face_kp, lhand_kp, rhand_kp))

            # --- 시각화 ---
            # body (초록)
            mp_drawing.draw_landmarks(
                frame, result.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            )
            # face (노랑)
            mp_drawing.draw_landmarks(
                frame, result.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1),
            )
            # left hand (파랑)
            mp_drawing.draw_landmarks(
                frame, result.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2),
            )
            # right hand (주황)
            mp_drawing.draw_landmarks(
                frame, result.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 128, 255), thickness=2, circle_radius=3),
                mp_drawing.DrawingSpec(color=(0, 128, 255), thickness=2),
            )

            # 프레임 번호
            cv2.putText(frame, f"Frame: {idx}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # 범례
            cv2.putText(frame, "Body",       (10, height - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),   2)
            cv2.putText(frame, "Left Hand",  (10, height - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0),   2)
            cv2.putText(frame, "Right Hand", (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 128, 255), 2)

            writer.write(frame)

            if (idx + 1) % 30 == 0:
                print(f"  {idx+1}/{total_frames} 프레임 처리 중...")
            idx += 1

    cap.release()
    writer.release()
    print(f"\n영상 저장 완료: {out_path}")

    # keypoint npy 저장 — shape: (frames, 543, 3)
    seq = np.array([
        np.concatenate([pose, face, lh, rh], axis=0)
        for pose, face, lh, rh in all_keypoints
    ])  # (frames, 543, 3)
    npy_path = base + "_keypoints.npy"
    np.save(npy_path, seq)
    print(f"keypoint 저장 완료: {npy_path}  shape: {seq.shape}")


if __name__ == "__main__":
    extract_and_save(VIDEO_PATH)
