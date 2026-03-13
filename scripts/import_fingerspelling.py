"""
mapping_fingerspelling.json을 읽어 sign_fingerspelling 테이블에 INSERT

실행 방법:
    python scripts/import_fingerspelling.py
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.databases.sign_session import SignSessionLocal, sign_engine, SignBase
from app.models.sign_fingerspelling import SignFingerspelling

MAPPING_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sign_data", "mapping_fingerspelling.json"
)


def main():
    if not os.path.exists(MAPPING_PATH):
        print(f"[ERROR] mapping_fingerspelling.json 없음: {MAPPING_PATH}")
        print("먼저 python sign_data/extract_all_fingerspelling.py 를 실행하세요.")
        return

    SignBase.metadata.create_all(bind=sign_engine)
    print("sign_fingerspelling 테이블 준비 완료")

    with open(MAPPING_PATH, encoding="utf-8") as f:
        mapping = json.load(f)

    db = SignSessionLocal()
    try:
        existing = db.query(SignFingerspelling).count()
        if existing > 0:
            print(f"기존 데이터 {existing}개 삭제 후 재삽입...")
            db.query(SignFingerspelling).delete()
            db.commit()

        for entry in mapping:
            db.add(SignFingerspelling(
                jamo         = entry["jamo"],
                duration_sec = entry["duration_sec"],
                frames       = entry["frames"],
                fps          = entry["fps"],
                npy_path     = entry["npy_path"],
            ))

        db.commit()
        print(f"\nDB INSERT 완료: {len(mapping)}개 행 저장")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
