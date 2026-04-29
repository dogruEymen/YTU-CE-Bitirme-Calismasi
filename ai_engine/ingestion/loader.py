from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from database.models import Article
from .schemas import RawArticleSchema

def _clean_string(val):
    if isinstance(val, str):
        return val.replace('\x00', '')
    return val

def save_articles_to_db(db_session: Session, articles: List[RawArticleSchema]) -> int:
    """
    Saves a list of articles to the database.
    Uses PostgreSQL UPSERT (ON CONFLICT DO NOTHING) to safely ignore duplicates based on external_id.
    """
    if not articles:
        return 0

    values = []
    for art in articles:
        d = art.to_dict()
        
        # Tüm string alanlardan NUL (\x00) karakterlerini temizle
        for k, v in d.items():
            d[k] = _clean_string(v)
            
        # Veritabanı modelindeki karakter sınırlarına göre kesme işlemi yap
        if d.get("title") and len(d["title"]) > 500:
            d["title"] = d["title"][:497] + "..."
        if d.get("external_id") and len(d["external_id"]) > 100:
            d["external_id"] = d["external_id"][:100]
        if d.get("pdf_url") and len(d["pdf_url"]) > 500:
            d["pdf_url"] = d["pdf_url"][:500]
        if d.get("primary_category") and len(d["primary_category"]) > 100:
            d["primary_category"] = d["primary_category"][:100]
        if d.get("source") and len(d["source"]) > 50:
            d["source"] = d["source"][:50]
            
        values.append(d)

    total_inserted = 0

    # PostgreSQL'in tek bir sorguda gönderebileceği parametre sınırını aşmamak için
    # verileri 1000'erli paketler (chunk) halinde kaydediyoruz.
    chunk_size = 1000
    for i in range(0, len(values), chunk_size):
        chunk = values[i:i+chunk_size]
        
        # Create the insert statement
        stmt = insert(Article).values(chunk)

        # If the external_id already exists, just ignore this insertion
        stmt = stmt.on_conflict_do_nothing(index_elements=['external_id'])

        # Execute
        result = db_session.execute(stmt)
        total_inserted += result.rowcount

    db_session.commit()
    return total_inserted
