import asyncio
import logging

from database.db import SessionLocal
from ai_engine.ingestion.extractors.arxiv_extractor import ArxivExtractor
from ai_engine.ingestion.extractors.openalex_extractor import OpenAlexExtractor
from ai_engine.ingestion.loader import save_articles_to_db

# Log ayarları
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    # Özel bir anahtar kelime olmadan (boş sorgu) tüm Computer Science makalelerini çekmek istiyoruz
    queries = [""]
    
    extractors = [
        ArxivExtractor(),
        OpenAlexExtractor()
    ]
    
    # Her sorgu ve her kaynak için maksimum kaç makale çekilecek?
    # 1 boş sorgu * 2 kaynak * 50.000 = Toplam 100.000 hedefi
    max_results_per_query = 10000 
    total_inserted = 0

    logger.info("=== 100.000 MAKALE ÇEKİMİ BAŞLIYOR ===")
    logger.info("Uyarı: Sistem 'ingestion_state.json' dosyasını kontrol ederek kaldığı yerden devam edecektir.")

    # Veritabanı bağlantısını başlat
    db = SessionLocal()

    try:
        for query in queries:
            logger.info(f"=== SORGULANIYOR: '{query}' ===")
            for extractor in extractors:
                logger.info(f"[{extractor.source_name.upper()}] API'sine istek atılıyor...")
                try:
                    # 1. Extract
                    articles = await extractor.fetch_articles(query, max_results=max_results_per_query)
                    logger.info(f"[{extractor.source_name.upper()}] {len(articles)} adet makale bulundu. Veritabanına yazılıyor...")
                    
                    # 2. Load
                    inserted = save_articles_to_db(db, articles)
                    total_inserted += inserted
                    logger.info(f"[{extractor.source_name.upper()}] Başarılı! {inserted} yeni makale eklendi. (Geri kalanı zaten mevcuttu)")
                    
                except Exception as e:
                    logger.error(f"[{extractor.source_name.upper()}] Hata oluştu: {e}")
                
                # Rate limitlere (hız sınırlarına) saygı duymak için bekleme süresi
                await asyncio.sleep(2)
                
    finally:
        db.close()
        logger.info(f"=== İŞLEM TAMAMLANDI. Veritabanına toplam {total_inserted} YENİ makale eklendi. ===")

if __name__ == "__main__":
    asyncio.run(main())
