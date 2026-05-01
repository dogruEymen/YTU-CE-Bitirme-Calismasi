import asyncio
from ai_engine.ingestion.extractors.arxiv_extractor import ArxivExtractor
from ai_engine.ingestion.extractors.openalex_extractor import OpenAlexExtractor
from ai_engine.ingestion.extractors.s2_extractor import SemanticScholarExtractor

async def main():
    query = "deep learning"
    max_res = 2
    
    print(f"--- Arama Sorgusu: '{query}' ---")
    
    # 1. ArXiv Test
    print("\n[1] ArXiv'den veri çekiliyor...")
    arxiv = ArxivExtractor()
    try:
        arxiv_results = await arxiv.fetch_articles(query, max_res)
        for idx, res in enumerate(arxiv_results):
            print(f"  {idx+1}. {res.title} (ID: {res.external_id})")
    except Exception as e:
        print(f"  HATA: {e}")

    await asyncio.sleep(1) # Rate limit koruması

    # 2. Semantic Scholar Test
    print("\n[2] Semantic Scholar'dan veri çekiliyor...")
    s2 = SemanticScholarExtractor()
    try:
        s2_results = await s2.fetch_articles(query, max_res)
        for idx, res in enumerate(s2_results):
            print(f"  {idx+1}. {res.title} (ID: {res.external_id})")
    except Exception as e:
        print(f"  HATA: {e}")

    await asyncio.sleep(1) # Rate limit koruması

    # 3. OpenAlex Test
    print("\n[3] OpenAlex'ten veri çekiliyor...")
    oa = OpenAlexExtractor()
    try:
        oa_results = await oa.fetch_articles(query, max_res)
        for idx, res in enumerate(oa_results):
            print(f"  {idx+1}. {res.title} (ID: {res.external_id})")
    except Exception as e:
        print(f"  HATA: {e}")

if __name__ == "__main__":
    asyncio.run(main())
