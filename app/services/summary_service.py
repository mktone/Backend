import anthropic

from app.core.config import settings

_SUMMARY_PROMPT = """\
당신은 한국어 뉴스 기사를 요약하는 전문가입니다.
주어진 기사 본문을 핵심 내용 위주로 4~5줄로 요약하세요.

[규칙]
- 핵심 정보만 간결하게 작성하세요.
- 불필요한 수식어나 감탄사는 제거하세요.
- 요약문만 출력하고 설명이나 부연은 하지 마세요.\
"""


async def summarize_article(body: str) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        temperature=0,
        system=_SUMMARY_PROMPT,
        messages=[{"role": "user", "content": body}],
    )
    return message.content[0].text
