"""
mapping.json을 읽어 수어 DB(sign_words 테이블)에 INSERT하는 스크립트

실행 방법:
    python scripts/import_sign.py
"""

import json
import os
import sys

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.databases.sign_session import SignSessionLocal, sign_engine
from app.models.sign_word import SignWord, SignBase

MAPPING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sign_data", "mapping.json"
)

# 진짜 동음이의어 word_num → category 번호
HOMONYM_CATEGORY = {
    "WORD0005": 1, "WORD1372": 2,   # 눈: 신체(1) / 날씨(2)
    "WORD1147": 1, "WORD2639": 2,   # 팔: 신체(1) / 숫자(2)
    "WORD0029": 1, "WORD1129": 2,   # 검사: 행위(1) / 직업(2)
    "WORD0236": 1, "WORD0408": 1,   # 지도: map(1)
    "WORD0413": 2, "WORD0768": 2,   # 지도: coaching(2)
    "WORD1588": 1, "WORD2178": 2,   # 구조: 짜임새(1) / 구해냄(2)
    "WORD0137": 1, "WORD0811": 2,   # 공식: 수식(1) / 공적(2)
    "WORD1483": 1, "WORD2866": 2,   # 이천: 지명(1) / 숫자(2)
}


def main():
    if not os.path.exists(MAPPING_PATH):
        print(f"[ERROR] mapping.json 없음: {MAPPING_PATH}")
        print("먼저 python sign_data/parse_keypoints.py 를 실행하세요.")
        return

    # 테이블 생성 (없으면 자동 생성)
    SignBase.metadata.create_all(bind=sign_engine)
    print("sign_words 테이블 준비 완료")

    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)

    db = SignSessionLocal()
    try:
        # 기존 데이터 초기화 (재실행 시 중복 방지)
        existing = db.query(SignWord).count()
        if existing > 0:
            print(f"기존 데이터 {existing}개 삭제 후 재삽입...")
            db.query(SignWord).delete()
            db.commit()

        total = 0
        for word, entries in mapping.items():
            for entry in entries:
                row = SignWord(
                    word         = word,
                    word_num     = entry["word_num"],
                    signer       = entry["signer"],
                    direction    = entry["direction"],
                    start        = entry["start"],
                    end          = entry["end"],
                    duration_sec = entry["duration_sec"],
                    frames       = entry["frames"],
                    fps          = entry["fps"],
                    npy_path     = entry["npy_path"],
                    category     = HOMONYM_CATEGORY.get(entry["word_num"]),
                )
                db.add(row)
                total += 1

        db.commit()
        print(f"\nDB INSERT 완료: {total}개 행 저장")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
