import json
import os
import sys

from bs4 import BeautifulSoup

# 프로젝트 루트를 sys.path에 추가 (독립 실행 지원)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.databases.news_session import SessionLocal, create_tables
from app.models.article import Article


def parse_body(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html.parser").get_text(separator="\n").strip()


def parse_keyword_list(keyword_list) -> str:
    if not keyword_list:
        return ""
    if isinstance(keyword_list, list):
        return ",".join(str(k) for k in keyword_list if k)
    return str(keyword_list)


def get_or_none(data: dict, *keys):
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    if data == "" or data is None:
        return None
    return data


def main():
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "01.매경뉴스json_2025",
        "2025",
    )

    json_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))

    total = len(json_files)
    saved = 0
    skipped = 0

    create_tables()
    db = SessionLocal()

    try:
        for idx, filepath in enumerate(json_files, 1):
            filename = os.path.basename(filepath)
            print(f"[{idx}/{total}] 처리 중: {filename}")

            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"  → 파일 읽기 오류: {e}")
                skipped += 1
                continue

            article_id = get_or_none(data, "article", "article_id")
            if article_id is None:
                skipped += 1
                continue

            # 중복 체크
            if db.query(Article).filter(Article.article_id == article_id).first():
                skipped += 1
                continue

            body_html = get_or_none(data, "article_body", "body")
            body_text = parse_body(body_html) if body_html else None

            article = Article(
                article_id=article_id,
                title=get_or_none(data, "article", "title"),
                writers=get_or_none(data, "article", "writers"),
                service_daytime=get_or_none(data, "article", "service_daytime"),
                main_category=get_or_none(data, "article", "main_category"),
                body=body_text,
                summary=get_or_none(data, "article_summary", "summary"),
                article_url=get_or_none(data, "article_url"),
                keyword_list=parse_keyword_list(data.get("keyword_list")),
                like_count=get_or_none(data, "share", "like_count"),
                reply_count=get_or_none(data, "share", "reply_count"),
            )

            db.add(article)
            try:
                db.commit()
                saved += 1
            except Exception as e:
                db.rollback()
                print(f"  → DB 저장 오류: {e}")
                skipped += 1

    finally:
        db.close()

    print(f"\n완료 - 저장: {saved}건 / 스킵: {skipped}건 / 전체: {total}건")


if __name__ == "__main__":
    main()
