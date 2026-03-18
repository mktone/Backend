from collections import defaultdict
from pathlib import Path
import re
import os

import numpy as np
from sqlalchemy.orm import Session

from app.models.sign_word import SignWord
from app.models.sign_fingerspelling import SignFingerspelling

# Backend 루트 (app/services/sign_service.py 기준 3단계 상위)
_BACKEND_ROOT = Path(__file__).parent.parent.parent

# ── 자모 분해 상수 ──────────────────────────────────────────────────────────────
_CHOSUNG  = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
_JUNGSUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
_JONGSUNG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

# DB에 없는 자모 → 분해 규칙
_EXPAND: dict[str, list[str]] = {
    'ㄲ': ['ㄱ','ㄱ'], 'ㄸ': ['ㄷ','ㄷ'], 'ㅃ': ['ㅂ','ㅂ'], 'ㅆ': ['ㅅ','ㅅ'], 'ㅉ': ['ㅈ','ㅈ'],
    'ㄳ': ['ㄱ','ㅅ'], 'ㄵ': ['ㄴ','ㅈ'], 'ㄶ': ['ㄴ','ㅎ'], 'ㄺ': ['ㄹ','ㄱ'], 'ㄻ': ['ㄹ','ㅁ'],
    'ㄼ': ['ㄹ','ㅂ'], 'ㄽ': ['ㄹ','ㅅ'], 'ㄾ': ['ㄹ','ㅌ'], 'ㄿ': ['ㄹ','ㅍ'], 'ㅀ': ['ㄹ','ㅎ'],
    'ㅄ': ['ㅂ','ㅅ'], 'ㅘ': ['ㅗ','ㅏ'], 'ㅙ': ['ㅗ','ㅐ'], 'ㅝ': ['ㅜ','ㅓ'], 'ㅞ': ['ㅜ','ㅔ'],
}

# DB에 있는 자모 세트 (extract_all_fingerspelling.py의 JAMO_ORDER 기준)
_DB_JAMO: set[str] = {
    'ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ',
    'ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅒ','ㅔ','ㅖ','ㅚ','ㅟ','ㅢ',
}

_FINGERSPELLING_RE = re.compile(r'\[지문자:\s*([^\]]+)\]')


def get_available_sign_words(db: Session) -> dict[str, list[int | None]]:
    """
    sign_db에서 사용 가능한 단어 목록 조회.
    Returns: {"단어": [category, ...]}
      예) {"눈": [1, 2], "약효": [None], "팔": [1, 2]}
    """
    try:
        rows = db.query(SignWord.word, SignWord.category).distinct(SignWord.word, SignWord.category).all()
    except Exception:
        return {}

    result: dict[str, set] = defaultdict(set)
    for word, category in rows:
        result[word].add(category)

    return {
        word: sorted(cats, key=lambda x: (x is None, x or 0))
        for word, cats in result.items()
    }


# ── Phase 1: 파싱 ───────────────────────────────────────────────────────────────

def parse_converted_text(text: str) -> list[dict]:
    """converted_text → [{type, word, category}] 토큰 리스트

    - [지문자: 단어] → type='fingerspelling'
    - 눈(2)         → type='word', category=2
    - 내리다         → type='word', category=None
    """
    text = text.replace('\n', ' ')
    tokens: list[dict] = []
    last = 0

    for m in _FINGERSPELLING_RE.finditer(text):
        # 지문자 패턴 앞의 일반 텍스트 처리
        _parse_plain(text[last:m.start()], tokens)
        tokens.append({'type': 'fingerspelling', 'word': m.group(1).strip(), 'category': None})
        last = m.end()

    _parse_plain(text[last:], tokens)
    return tokens


def _parse_plain(text: str, tokens: list[dict]) -> None:
    for raw in text.split():
        token = raw.strip('!?~;:…')
        if not token:
            continue
        m = re.match(r'^(.+?)\s*\((\d+)\)$', token)
        if m:
            tokens.append({'type': 'word', 'word': m.group(1), 'category': int(m.group(2))})
        else:
            tokens.append({'type': 'word', 'word': token, 'category': None})


# ── Phase 2: DB 조회 + npy 로드 ─────────────────────────────────────────────────

def _load_npy(npy_path: str) -> list | None:
    full = _BACKEND_ROOT / npy_path.replace('/', os.sep)
    if not full.exists():
        return None
    return np.load(str(full)).tolist()


def lookup_word(db: Session, word: str, category: int | None) -> dict | None:
    """sign_words DB 조회. direction 우선순위: F → D → first"""
    q = db.query(SignWord).filter(SignWord.word == word)
    if category is not None:
        q = q.filter(SignWord.category == category)

    rows = q.all()
    if not rows:
        return None

    row = (
        next((r for r in rows if r.direction == 'F'), None)
        or next((r for r in rows if r.direction == 'D'), None)
        or rows[0]
    )

    frames = _load_npy(row.npy_path)
    if frames is None:
        return None

    return {'type': 'word', 'word': word, 'fps': row.fps, 'frames': frames}


# ── Phase 3: 자모 분해 + fingerspelling DB 조회 ─────────────────────────────────

def _decompose_syllable(char: str) -> list[str]:
    code = ord(char) - 0xAC00
    if code < 0 or code > 0xD7A3 - 0xAC00:
        return []

    cho  = _CHOSUNG[code // (21 * 28)]
    jung = _JUNGSUNG[(code % (21 * 28)) // 28]
    jong = _JONGSUNG[code % 28]

    result: list[str] = []
    result.extend(_EXPAND.get(cho,  [cho])  if cho  not in _DB_JAMO else [cho])
    result.extend(_EXPAND.get(jung, [jung]) if jung not in _DB_JAMO else [jung])
    if jong:
        result.extend(_EXPAND.get(jong, [jong]) if jong not in _DB_JAMO else [jong])
    return result


def decompose_to_jamo(word: str) -> list[str]:
    """한글 단어 → DB에 있는 자모 리스트"""
    jamo: list[str] = []
    for char in word:
        if '\uAC00' <= char <= '\uD7A3':
            jamo.extend(_decompose_syllable(char))
        # 공백/영어/숫자는 skip
    return jamo


def lookup_fingerspelling(db: Session, word: str) -> list[dict]:
    """단어를 자모 분해하고 각 자모의 fingerspelling segment 반환"""
    segments: list[dict] = []
    for jamo in decompose_to_jamo(word):
        row = db.query(SignFingerspelling).filter(SignFingerspelling.jamo == jamo).first()
        if row is None:
            continue
        frames = _load_npy(row.npy_path)
        if frames is None:
            continue
        segments.append({'type': 'fingerspelling', 'word': jamo, 'fps': row.fps, 'frames': frames})
    return segments


# ── 메인: Phase 1~4 통합 ────────────────────────────────────────────────────────

def get_sign_segments(db: Session, text: str) -> list[dict]:
    """converted_text → segments 리스트 (Phase 1~4)"""
    segments: list[dict] = []

    for token in parse_converted_text(text):
        if token['type'] == 'fingerspelling':
            # [지문자: 단어] → 자모 분해
            segments.extend(lookup_fingerspelling(db, token['word']))
        else:
            # word → DB 조회, miss 시 지문자 fallback
            result = lookup_word(db, token['word'], token['category'])
            if result:
                segments.append(result)
            else:
                segments.extend(lookup_fingerspelling(db, token['word']))

    return segments
