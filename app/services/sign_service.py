from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.sign_word import SignWord


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
