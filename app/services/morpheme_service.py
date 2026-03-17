import re

from kiwipiepy import Kiwi

_kiwi = Kiwi()

# NNG: 일반명사, NNP: 고유명사, NR: 수사, VV: 동사, VA: 형용사, XR: 어근
_NOUN_POS = {"NNG", "NNP", "NR"}
_VERB_POS = {"VV", "VA", "XR"}

_FINGERSPELLING_PATTERN = re.compile(r'(\{[^}]+\})')

# 제거할 품사
_REMOVE_POS = {
    "JKS", "JKO", "JKB", "JKG", "JKC", "JKV", "JKQ",  # 격조사
    "JX", "JC",                                          # 보조사, 접속조사
    "EF", "EC", "EP", "ETM", "ETN",                     # 어미 전체 (수어에서 불필요)
    "XSV", "XSA",                                        # 동사/형용사 파생접미사 "하다" (수어에서 명사/어근만 표현)
    "VCP",                                               # 긍정지정사 "이다"
}

# 기본형 "다"를 붙일 품사 (동사/형용사 어간)
_VERB_BASE_POS = {"VV", "VA", "VX"}

_SINO_DIGITS = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_UNITS = [(10000, "만"), (1000, "천"), (100, "백"), (10, "십")]


def _number_to_korean(n: int) -> str:
    """숫자를 한자어 복합 표기로 변환. 예) 50→'오십', 109→'백구'"""
    if n == 0:
        return "영"
    result = ""
    for unit_val, unit_name in _UNITS:
        if n >= unit_val:
            q = n // unit_val
            result += (_SINO_DIGITS[q] if q > 1 else "") + unit_name
            n %= unit_val
    if n > 0:
        result += _SINO_DIGITS[n]
    return result


def _convert_number(num_str: str, sign_word_set: set) -> str:
    """숫자 문자열을 sign_db 기반 한국어 수 표현으로 변환."""
    n = int(num_str)
    korean = _number_to_korean(n)
    if korean in sign_word_set:
        return korean

    parts = []
    remaining = n
    for unit_val, unit_name in _UNITS:
        if remaining >= unit_val:
            q = remaining // unit_val
            remaining %= unit_val
            compound = (_SINO_DIGITS[q] if q > 1 else "") + unit_name
            if compound in sign_word_set:
                parts.append(compound)
            else:
                if q > 1 and _SINO_DIGITS[q] in sign_word_set:
                    parts.append(_SINO_DIGITS[q])
                if unit_name in sign_word_set:
                    parts.append(unit_name)
    if remaining > 0:
        digit_word = _SINO_DIGITS[remaining]
        if digit_word in sign_word_set:
            parts.append(digit_word)
    return " ".join(parts) if parts else korean


_NO_SPACE_BEFORE = {"SF", "SP", "SSC", "SE", "SO", "SW"}
_NO_SPACE_AFTER = {"SSO"}


def preprocess_remove_particles(text: str) -> str:
    """토큰 단위로 재조합하여 조사/어미를 제거하고 숫자를 한국어로 변환합니다.
    복합어도 분리됩니다. 예) '눈호강' → '눈 호강', '50년간' → '오십 년간'
    """
    tokens = _kiwi.tokenize(text)
    parts: list[tuple[str, str]] = []  # (tag, form)

    for token in tokens:
        if token.tag in _REMOVE_POS:
            continue
        form = token.form
        if token.tag == "SN":
            try:
                form = _number_to_korean(int(form))
            except (ValueError, OverflowError):
                pass
        elif token.tag in _VERB_BASE_POS:
            form = form + "다"  # 어간 → 기본형: "쫓" → "쫓다"
        parts.append((token.tag, form))

    result = []
    for i, (tag, form) in enumerate(parts):
        if i == 0:
            result.append(form)
        elif tag in _NO_SPACE_BEFORE or (i > 0 and parts[i - 1][0] in _NO_SPACE_AFTER):
            result.append(form)
        else:
            result.append(" " + form)

    return re.sub(r"\s+", " ", "".join(result)).strip()


def _to_lemma(form: str, tag: str) -> list[str]:
    """형태소를 sign_db 매칭용 후보 단어 목록으로 변환합니다."""
    candidates = [form]
    if tag in _VERB_POS:
        candidates.append(form + "다")
        if tag == "XR":
            candidates.append(form + "하다")
    return candidates


def match_sign_words(
    text: str, sign_words: dict[str, list]
) -> tuple[set[str], set[str]]:
    """텍스트에서 형태소를 추출하고 sign_db 단어 목록과 매칭합니다."""
    tokens = _kiwi.tokenize(text)

    available: set[str] = set()
    unavailable: set[str] = set()

    for token in tokens:
        if token.tag not in _NOUN_POS and token.tag not in _VERB_POS:
            continue

        candidates = _to_lemma(token.form, token.tag)
        matched = next((c for c in candidates if c in sign_words), None)

        if matched:
            available.add(matched)
        else:
            unavailable.add(candidates[-1])

    return available, unavailable


def postprocess_converted_text(text: str, sign_words: dict[str, list]) -> str:
    """Claude가 변환한 텍스트를 후처리합니다.
    Claude 출력의 {단어} 형식을 [지문자: 단어]로 변환하고,
    나머지 한글 단어는 sign_db 기준으로 처리합니다.
    """
    sign_word_set = set(sign_words.keys())
    parts = _FINGERSPELLING_PATTERN.split(text)

    result = []
    for part in parts:
        if _FINGERSPELLING_PATTERN.match(part):
            # {단어} → [지문자: 단어]
            word = part[1:-1]
            result.append(f"[지문자: {word}]")
        else:
            result.append(_replace_non_sign_words(part, sign_word_set))

    return "".join(result)


def _replace_non_sign_words(text: str, sign_word_set: set) -> str:
    result = []
    last_end = 0

    for m in re.finditer(r"[가-힣]+|(?<!\()\d+(?!\))", text):
        result.append(text[last_end:m.start()])
        word = m.group()

        if word.isdigit():
            result.append(_convert_number(word, sign_word_set))
        elif word in sign_word_set:
            result.append(word)
        else:
            base_da = word + "다"
            base_hada = word + "하다"
            if base_da in sign_word_set:
                result.append(base_da)
            elif base_hada in sign_word_set:
                result.append(base_hada)
            else:
                result.append(f"[지문자: {word}]")

        last_end = m.end()

    result.append(text[last_end:])
    return "".join(result)
