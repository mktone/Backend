# Backend

## 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.11
- 매경 뉴스 JSON 데이터 (`01.매경뉴스json_2025/` 폴더) → 프로젝트 루트(`Backend/`)에 위치해야 합니다

```
Backend/
├── 01.매경뉴스json_2025/   ← 여기에 위치
│   ├── *.json
├── app/
├── scripts/
├── docker-compose.yml
└── ...
```

## 시작하기

### 1. .env 파일 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채워주세요.

```
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=설정할비밀번호
DB_NAME=news_db

SIGN_DB_HOST=localhost
SIGN_DB_PORT=3308
SIGN_DB_USER=root
SIGN_DB_PASSWORD=설정할비밀번호
SIGN_DB_NAME=sign_db

ANTHROPIC_API_KEY=발급받은키
```

### 2. 실행

```bash
docker-compose up --build
```

### 3. JSON 데이터 임포트 (최초 1회)

Docker DB가 실행 중인 상태에서 아래 명령어를 실행합니다.

```bash
python -m venv .venv
venv\Scripts\activate
pip install -r requirements.txt
python scripts/import_json.py
```

### 4. API 확인

브라우저에서 아래 주소로 Swagger UI에 접속합니다.

```
http://localhost:8000/docs
```

> **참고 - 서버 시작 시 동작**
> - 한국어 임베딩 모델(`jhgan/ko-sroberta-multitask`) 로딩 (최초 1회 다운로드)
> - sign_db 단어 임베딩 벡터 계산 (수십 초 소요)
>
> **`/api/v1/convert` 동작 방식**
> - 형태소 분석으로 sign_db 단어와 정확한 매칭 먼저 수행
> - 매칭 안 된 단어는 임베딩 유사도로 sign_db에서 가장 유사한 단어 탐색
>   예) "재미있다" → sign_db에 "흥미롭다"가 있으면 자동 대체
> - 유사 단어도 없는 경우만 `[지문자: 단어]` 형식으로 표시
