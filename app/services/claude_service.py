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
4. 핵심 내용은 유지하고 최소한의 문법 변환만 수행하세요.

[단어 처리 규칙]
- [수어 가능 단어 목록]에 있는 단어는 그대로 사용하세요.
- [지문자 처리 단어 목록]에 있는 단어는 중괄호로 표시하세요. 예) {섀도우}, {블록버스터}
- 두 목록 모두에 없는 단어도 중괄호로 표시하세요. 예) {히어로}, {스피드}
- [동음이의어] 목록의 단어는 문맥에 맞는 번호를 붙여 사용하세요.
  예) 눈(1) → 신체의 눈(eye), 눈(2) → 날씨의 눈(snow)

[출력 형식]
- 변환된 수어 문법 텍스트만 출력하세요.
- 설명이나 부연 설명 없이 변환 결과만 출력하세요.\
"""


def _build_system_prompt(
    sign_words: dict[str, list[int | None]],
    available: set[str],
    unavailable: set[str],
    replacements: dict[str, str] | None = None,
) -> str:
    homonyms: list[str] = []
    for word in available:
        if word not in sign_words:
            continue
        real_cats = [c for c in sign_words[word] if c is not None]
        if len(real_cats) > 1:
            if word in HOMONYM_INFO:
                desc = ", ".join(
                    f"{c}={HOMONYM_INFO[word][c]}"
                    for c in real_cats
                    if c in HOMONYM_INFO[word]
                )
                homonyms.append(f"{word} (동음이의어: {desc})")
            else:
                homonyms.append(f"{word} (카테고리: {', '.join(str(c) for c in real_cats)})")

    prompt = _BASE_PROMPT

    if available:
        prompt += "\n\n[수어 가능 단어 목록]\n"
        prompt += ", ".join(sorted(available)) + "\n"

    if homonyms:
        prompt += "\n[동음이의어]\n" + "\n".join(f"  - {h}" for h in homonyms) + "\n"

    if unavailable:
        prompt += "\n\n[지문자 처리 단어 목록]\n"
        prompt += ", ".join(sorted(unavailable)) + "\n"

    return prompt


def convert_to_sign_language(
    body: str,
    sign_words: dict[str, list[int | None]],
    available: set[str],
    unavailable: set[str],
    replacements: dict[str, str] | None = None,
) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    system_prompt = _build_system_prompt(sign_words, available, unavailable, replacements)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": body}],
    )
    return message.content[0].text
