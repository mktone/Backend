"""
수어 키포인트 시각화 스크립트
사용법: python3 sign_data/visualize_sign.py 눈
        python3 sign_data/visualize_sign.py 지도   ← 4개도 자동 처리

- 스페이스바: 재생/일시정지
- 방향키 좌/우: 프레임 이동
- q: 종료
"""

import sys
import os
import glob
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DB_DIR       = os.path.join(BASE_DIR, "word_motion_db")
MAPPING_PATH = os.path.join(BASE_DIR, "mapping.json")

POSE_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),
    (0,12),(12,13),(13,14),
    (0,15),(15,17),
    (0,16),(16,18),
]

HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
]


def draw_skeleton(ax, frame, title=""):
    ax.clear()
    ax.set_xlim(0, 1920)
    ax.set_ylim(1080, 0)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9)
    ax.axis('off')

    pose  = frame[0:25]
    lhand = frame[95:116]
    rhand = frame[116:137]

    for a, b in POSE_CONNECTIONS:
        if pose[a].any() and pose[b].any():
            ax.plot([pose[a][0], pose[b][0]], [pose[a][1], pose[b][1]], 'b-', lw=1.5)
    ax.scatter(pose[:,0], pose[:,1], c='blue', s=20, zorder=5)

    for a, b in HAND_CONNECTIONS:
        if lhand[a].any() and lhand[b].any():
            ax.plot([lhand[a][0], lhand[b][0]], [lhand[a][1], lhand[b][1]], 'g-', lw=1.5)
    ax.scatter(lhand[:,0], lhand[:,1], c='green', s=15, zorder=5)

    for a, b in HAND_CONNECTIONS:
        if rhand[a].any() and rhand[b].any():
            ax.plot([rhand[a][0], rhand[b][0]], [rhand[a][1], rhand[b][1]], 'r-', lw=1.5)
    ax.scatter(rhand[:,0], rhand[:,1], c='red', s=15, zorder=5)


def load_npy(word, word_num, direction="F"):
    pattern = os.path.join(DB_DIR, f"{word}_{word_num}_*_{direction}.npy")
    files = glob.glob(pattern)
    if not files:
        files = glob.glob(os.path.join(DB_DIR, f"{word}_{word_num}_*.npy"))
    return np.load(files[0]) if files else None


def main():
    word = sys.argv[1] if len(sys.argv) > 1 else "눈"

    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)

    if word not in mapping:
        print(f"'{word}' 단어를 찾을 수 없습니다.")
        return

    word_nums = sorted({e["word_num"] for e in mapping[word]})
    n = len(word_nums)

    motions = []
    for wn in word_nums:
        m = load_npy(word, wn)
        if m is None:
            print(f"{wn} npy 파일 없음, 건너뜀")
        else:
            motions.append((wn, m))

    if not motions:
        print("npy 파일을 찾을 수 없습니다.")
        return

    n = len(motions)
    cols = min(n, 4)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 6 * rows))
    fig.suptitle(f"수어 비교: '{word}' ({n}개 word_num)", fontsize=13)

    # axes를 항상 리스트로
    if n == 1:
        axes = [axes]
    elif rows == 1:
        axes = list(axes)
    else:
        axes = [ax for row in axes for ax in row]

    # 남는 axes 숨기기
    for i in range(n, len(axes)):
        axes[i].axis('off')

    state = {"frame": 0, "playing": True}
    max_frames = max(len(m) for _, m in motions)

    def update(frame_idx):
        for i, (wn, motion) in enumerate(motions):
            fi = min(frame_idx, len(motion) - 1)
            draw_skeleton(axes[i], motion[fi], f"{wn}\n(frame {fi+1}/{len(motion)})")
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == ' ':
            state["playing"] = not state["playing"]
        elif event.key == 'right':
            state["frame"] = min(state["frame"] + 1, max_frames - 1)
            update(state["frame"])
        elif event.key == 'left':
            state["frame"] = max(state["frame"] - 1, 0)
            update(state["frame"])
        elif event.key == 'q':
            plt.close()

    fig.canvas.mpl_connect('key_press_event', on_key)

    def animate(_):
        if state["playing"]:
            state["frame"] = (state["frame"] + 1) % max_frames
            update(state["frame"])

    ani = animation.FuncAnimation(fig, animate, interval=80, cache_frame_data=False)
    update(0)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
