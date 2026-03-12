import json
import numpy as np
import os
import glob
from collections import defaultdict

# 스크립트 위치 기준 상대경로
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
KEYPOINT_DIR  = os.path.join(BASE_DIR, "수어영상", "01")
MORPHEME_BASE = os.path.join(BASE_DIR, "수어영상", "morpheme")
OUTPUT_DIR    = os.path.join(BASE_DIR, "word_motion_db")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_keypoints_from_frame(json_path):
    """프레임 JSON에서 3D 키포인트 추출 → shape: (137, 3)

    2D가 필요하면 motion[:, :, :2] 로 슬라이싱
    """
    with open(json_path) as f:
        d = json.load(f)

    people = d["people"]

    def parse_kp(flat_list, n_points):
        arr = np.array(flat_list, dtype=np.float32).reshape(n_points, 4)
        return arr[:, :3]  # x, y, z (confidence 제거)

    pose  = parse_kp(people["pose_keypoints_3d"],       25)
    face  = parse_kp(people["face_keypoints_3d"],       70)
    lhand = parse_kp(people["hand_left_keypoints_3d"],  21)
    rhand = parse_kp(people["hand_right_keypoints_3d"], 21)

    return np.concatenate([pose, face, lhand, rhand], axis=0)  # (137, 3)


def process_word(morpheme_path):
    """morpheme JSON 하나 → npy 저장 + meta 반환"""
    with open(morpheme_path, encoding="utf-8") as f:
        meta = json.load(f)

    if not meta.get("data") or not meta["data"][0].get("attributes"):
        return None

    word       = meta["data"][0]["attributes"][0]["name"]
    start_time = meta["data"][0]["start"]
    end_time   = meta["data"][0]["end"]
    duration   = meta["metaData"]["duration"]

    # 파일명에서 word_num, signer, direction 추출
    # 예: NIA_SL_WORD2145_REAL03_L_morpheme.json → WORD2145, REAL03, L
    base_name = os.path.basename(morpheme_path).replace("_morpheme.json", "")
    parts     = base_name.split("_")
    word_num  = next((p for p in parts if p.startswith("WORD")), "UNKNOWN")
    signer    = next((p for p in parts if p.startswith("REAL")), "UNKNOWN")
    direction = parts[-1]  # D, F, L, R, U

    # 대응하는 keypoint 폴더
    kp_folder = os.path.join(KEYPOINT_DIR, base_name)

    if not os.path.exists(kp_folder):
        return None

    frame_files  = sorted(glob.glob(os.path.join(kp_folder, "*_keypoints.json")))
    total_frames = len(frame_files)

    if total_frames == 0:
        return None

    if duration <= 0:
        return None

    fps         = total_frames / duration
    start_frame = max(0, int(round(start_time * fps)))
    end_frame   = min(total_frames - 1, int(round(end_time * fps)))

    frames = []
    for i in range(start_frame, end_frame + 1):
        try:
            kp = extract_keypoints_from_frame(frame_files[i])
            frames.append(kp)
        except Exception as e:
            print(f"[WARN] 프레임 {i} 파싱 오류: {e}")

    if len(frames) == 0:
        return None

    motion = np.array(frames)  # (frames, 137, 3)

    save_name = f"{word}_{word_num}_{signer}_{direction}.npy"
    save_path = os.path.join(OUTPUT_DIR, save_name)
    np.save(save_path, motion)

    meta_entry = {
        "npy_path":     os.path.join("sign_data", "word_motion_db", save_name),
        "word_num":     word_num,
        "signer":       signer,
        "direction":    direction,
        "start":        round(start_time, 3),
        "end":          round(end_time, 3),
        "duration_sec": round(end_time - start_time, 3),
        "frames":       int(motion.shape[0]),
        "fps":          round(fps, 4),
    }
    return word, meta_entry


def build_mapping(meta_records):
    """수집된 meta_records → mapping.json 생성

    구조:
    {
      "약효": [
        {
          "npy_path": "...",
          "word_num": "WORD2145",
          "signer": "REAL01",
          "direction": "F",
          "start": 1.482,
          "end": 2.963,
          "duration_sec": 1.481,
          "frames": 44,
          "fps": 29.97
        },
        ...
      ],
      ...
    }
    """
    mapping = {
        w: sorted(entries, key=lambda e: (e["word_num"], e["signer"], e["direction"]))
        for w, entries in sorted(meta_records.items())
    }

    mapping_path = os.path.join(BASE_DIR, "mapping.json")
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    homonyms = {w: es for w, es in mapping.items() if len({e["word_num"] for e in es}) > 1}
    print(f"\nmapping.json 저장 완료: {len(mapping)}개 단어, 동음이의어 {len(homonyms)}개")
    return mapping


def main():
    # 기존 npy 파일 초기화 (재실행 시 중복 방지)
    existing = glob.glob(os.path.join(OUTPUT_DIR, "*.npy"))
    if existing:
        print(f"기존 .npy 파일 {len(existing)}개 삭제 후 재생성...")
        for f in existing:
            os.remove(f)

    # morpheme/01 ~ morpheme/16 모든 폴더 수집
    morpheme_dirs = sorted(glob.glob(os.path.join(MORPHEME_BASE, "*")))
    all_files = []
    for mdir in morpheme_dirs:
        files = sorted(glob.glob(os.path.join(mdir, "*_morpheme.json")))
        all_files.extend(files)

    print(f"처리할 전체 파일 수: {len(all_files)}")

    meta_records = defaultdict(list)
    success, fail = 0, 0

    for i, mpath in enumerate(all_files):
        result = process_word(mpath)
        if result:
            word, meta_entry = result
            meta_records[word].append(meta_entry)
            print(f"[{i+1}/{len(all_files)}] {word} | {meta_entry['signer']} {meta_entry['direction']} → {meta_entry['frames']}frames")
            success += 1
        else:
            fail += 1

    print(f"\n완료: 성공 {success}개, 실패 {fail}개")
    build_mapping(meta_records)


if __name__ == "__main__":
    main()
