import anthropic

from app.core.config import settings

SYSTEM_PROMPT = """당신은 한국어 텍스트를 한국수어 문법에 맞게 변환하는 전문가입니다.
한국수어는 한국어와 다른 독립적인 언어로, 다음 특성을 가집니다:
1. 어순: 한국어(주어-목적어-서술어)와 동일하지만 더 단순하게
2. 조사 생략: 은/는/이/가/을/를 등 조사 제거
3. 단순화: 복잡한 문장을 짧고 단순한 문장으로 분리
4. 쉬운 단어: 어려운 한자어/전문용어를 쉬운 단어로 교체
5. 구체적 표현: 추상적 표현을 구체적으로 변환
변환 시 원문의 핵심 의미는 반드시 유지하세요."""


def convert_to_sign_language(body: str) -> str:
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": body}
        ],
    )

    return message.content[0].text
