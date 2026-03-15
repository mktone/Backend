import anthropic

from app.core.config import settings

# README에 명시된 동음이의어 카테고리별 의미
HOMONYM_INFO: dict[str, dict[int, str]] = {
    "눈":  {1: "신체(eye)", 2: "날씨(snow)"},
    "팔":  {1: "신체(arm)", 2: "숫자(8)"},
    "검사": {1: "행위(inspection)", 2: "직업(prosecutor)"},
    "지도": {1: "지도(map)", 2: "가르침(coaching)"},
    "구조": {1: "짜임새(structure)", 2: "구해냄(rescue)"},
    "공식": {1: "수식(formula)", 2: "공적(official)"},
    "이천": {1: "지명(Icheon)", 2: "숫자(2000)"},
}

_BASE_PROMPT = """\
당신은 한국어 뉴스를 한국수어(KSL) 문법에 맞게 변환하는 전문가입니다.

[한국수어 문법 규칙]
1. 주어-목적어-동사 어순(SOV)
2. 조사, 어미, 접속사 생략
3. 시제는 시간 부사로 표현 (어제, 내일, 지금 등)
4. 불필요한 수식어 제거, 핵심 의미만 전달
5. 복잡한 한자어·전문용어는 쉬운 말로 풀어쓰기

[단어 처리 규칙]
- 아래 "수어 DB 단어 목록"에 있는 단어는 그대로 사용하세요.
- 목록에 없는 단어라도 목록에 있는 유사한 단어나 기본형으로 대체할 수 있으면 대체하세요.
  예) "보여준다" → 목록에 "보다"가 있으면 "보다"로 대체
  예) "달려가고" → 목록에 "달리다"가 있으면 "달리다"로 대체
  예) "아름다운" → 목록에 "아름답다"가 있으면 "아름답다"로 대체
- 유사 단어로도 대체할 수 없는 단어만 [지문자: 단어] 형식으로 표시하세요.
- 동음이의어(카테고리가 있는 단어)는 문맥에 맞는 번호를 괄호에 넣어 표시하세요.
  예) 눈(1) → 신체의 눈(eye), 눈(2) → 날씨의 눈(snow)

[출력 형식]
- 변환된 수어 문법 텍스트만 출력하세요.
- 설명이나 부연 설명 없이 변환 결과만 출력하세요.\
"""


def _build_system_prompt(sign_words: dict[str, list[int | None]]) -> str:
    if not sign_words:
        return _BASE_PROMPT + "\n\n[수어 DB 단어 목록]\n(단어 목록 없음 - 모든 단어를 [지문자: 단어] 형식으로 표시)"

    regular: list[str] = []
    homonyms: list[str] = []

    for word, categories in sign_words.items():
        real_cats = [c for c in categories if c is not None]
        if len(real_cats) <= 1:
            regular.append(word)
        else:
            if word in HOMONYM_INFO:
                desc = ", ".join(
                    f"{c}={HOMONYM_INFO[word][c]}"
                    for c in real_cats
                    if c in HOMONYM_INFO[word]
                )
                homonyms.append(f"{word} (동음이의어: {desc})")
            else:
                homonyms.append(f"{word} (카테고리: {', '.join(str(c) for c in real_cats)})")

    word_list_section = "\n\n[수어 DB 단어 목록]\n"
    if regular:
        word_list_section += "일반 단어: " + ", ".join(sorted(regular)) + "\n"
    if homonyms:
        word_list_section += "동음이의어:\n" + "\n".join(f"  - {h}" for h in homonyms) + "\n"

    return _BASE_PROMPT + word_list_section


def convert_to_sign_language(body: str, sign_words: dict[str, list[int | None]]) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    system_prompt = _build_system_prompt(sign_words)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": body}],
    )
    return message.content[0].text
