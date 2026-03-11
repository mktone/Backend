# sign_data

수어 키포인트 데이터를 파싱하여 `.npy` 파일과 `mapping.json`을 생성하고, DB에 저장하는 모듈입니다.

---

## 폴더 구조

```
sign_data/
├── parse_keypoints.py     ← 데이터 파싱 스크립트
├── mapping.json           ← 파싱 후 자동 생성됨
├── README.md
├── 수어영상/               ← ❌ git 미포함 (Google Drive에서 받을 것)
│   ├── 01/               ← 키포인트 JSON 데이터 (REAL01)
│   │   ├── NIA_SL_WORD0001_REAL01_D/
│   │   ├── NIA_SL_WORD0001_REAL01_F/
│   │   └── ...
│   └── morpheme/         ← 단어 라벨 + 타이밍 데이터 (16명)
│       ├── 01/
│       ├── 02/
│       └── ...
└── word_motion_db/        ← ❌ git 미포함 (파싱 후 자동 생성)
    ├── 약효_WORD2145_REAL01_F.npy
    └── ...
```

---

## 데이터 다운로드

**AI hub** 링크에서 `수어영상` 폴더를 받아 아래 경로에 배치:

```
[다운받을 데이터]
01_real_word_keypoint.zip
01_real_word_morpheme.zip

[경로]
mkton/Backend/sign_data/수어영상/
```

> 현재 보유 데이터: REAL01 키포인트 (5방향), 전체 16명 morpheme 라벨

---

## 실행 순서

> 모든 명령어는 `Backend/` 폴더에서 실행

### 1. 패키지 설치

```bash
pip3 install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일 열어서 아래처럼 채우기:
```
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=1234
DB_NAME=news_db

SIGN_DB_HOST=localhost
SIGN_DB_PORT=3308
SIGN_DB_USER=root
SIGN_DB_PASSWORD=1234
SIGN_DB_NAME=sign_db
```


### 3. DB 컨테이너 실행

```bash
docker-compose up -d db sign_db
```

컨테이너 상태 확인:
```bash
docker ps
```
`hackathon_news_db`, `sign_language_db` 둘 다 `healthy` 상태면 정상

### 4. 키포인트 파싱 (npy + mapping.json 생성)

```bash
python3 sign_data/parse_keypoints.py
```

> ⏳ 시간이 걸려요 (약 15,000개 처리). 터미널에서 진행 상황 확인 가능.

완료 후 생성되는 파일:
- `sign_data/word_motion_db/*.npy` - 단어별 키포인트 시퀀스
- `sign_data/mapping.json` - 단어 → npy 경로/메타 매핑

### 5. DB에 데이터 저장

```bash
python3 scripts/import_sign.py
```

완료 메시지: `DB INSERT 완료: 15000개 행 저장`

### 6. DB 확인 (MySQL Workbench)

| 항목 | 값 |
|---|---|
| Hostname | 127.0.0.1 |
| Port | 3308 |
| Username | root |
| Password | 1234 |

접속 후 확인:
```sql
USE sign_db;
SELECT * FROM sign_words LIMIT 20;
```

---

## mapping.json 구조

```json
{
  "약효": [
    {
      "npy_path": "/path/to/약효_WORD2145_REAL01_F.npy",
      "word_num": "WORD2145",
      "signer": "REAL01",
      "direction": "F",
      "start": 1.482,
      "end": 2.963,
      "duration_sec": 1.481,
      "frames": 44,
      "fps": 29.97
    }
  ]
}
```

| 필드 | 설명 |
|---|---|
| `npy_path` | npy 파일 경로 |
| `word_num` | 수어 단어 고유 번호 (동음이의어 구분) |
| `signer` | 화자 ID (REAL01 ~ REAL16) |
| `direction` | 촬영 방향 (D/F/L/R/U) |
| `start` / `end` | 수어 시작/종료 시각 (초) |
| `duration_sec` | 수어 진행 시간 (end - start) |
| `frames` | 프레임 수 |
| `fps` | 초당 프레임 수 |

---

## npy 파일 형식

```
shape: (frames, 137, 2)
  - frames: 해당 수어의 프레임 수
  - 137: 관절 수 (pose 25 + face 70 + 왼손 21 + 오른손 21)
  - 2: x, y 좌표
```
