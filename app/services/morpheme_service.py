from kiwipiepy import Kiwi
from app.services.embedding_service import embedding_service

_kiwi = Kiwi()

# NNG: 일반명사, NNP: 고유명사, VV: 동사, VA: 형용사, XR: 어근
_NOUN_POS = {"NNG", "NNP"}
_VERB_POS = {"VV", "VA", "XR"}


def _to_lemma(form: str, tag: str) -> list[str]:
    """
    형태소를 sign_db 매칭용 후보 단어 목록으로 변환합니다.
    동사/형용사는 '다'를 붙인 기본형도 후보에 포함합니다.
    예) "보이" (VV) → ["보이", "보이다"]
    """
    candidates = [form]
    if tag in _VERB_POS:
        candidates.append(form + "다")
    return candidates


def match_sign_words(text: str, sign_words: dict[str, list]) -> tuple[set[str], set[str]]:
    """
    텍스트에서 형태소를 추출하고 sign_db 단어 목록과 매칭합니다.

    Returns:
        (available, unavailable)
        - available: sign_db에 있는 단어 (기본형)
        - unavailable: sign_db에 없는 단어 (지문자 처리 필요)
    """
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
            # 임베딩 유사도로 sign_db에서 가장 유사한 단어 탐색
            similar = embedding_service.find_similar(candidates[-1])
            if similar:
                available.add(similar)
            else:
                # 명사는 그대로, 동사/형용사는 기본형(다 붙인 것)으로 표시
                unavailable.add(candidates[-1])

    return available, unavailable
