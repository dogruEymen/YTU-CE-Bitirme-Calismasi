import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional
import urllib.parse

from .base import BaseExtractor
from ..schemas import RawArticleSchema
from ..state_manager import load_state, save_state

class ArxivExtractor(BaseExtractor):
    BASE_URL = "https://export.arxiv.org/api/query"
    
    @property
    def source_name(self) -> str:
        return "arxiv"

    def _parse_entry(self, entry: ET.Element, namespace: dict) -> RawArticleSchema:
        """Parses an Atom entry from arXiv into a RawArticleSchema."""
        external_id = entry.find("atom:id", namespace).text.split("/")[-1]
        title = entry.find("atom:title", namespace).text.replace("\n", " ").strip()
        abstract_text = entry.find("atom:summary", namespace).text.replace("\n", " ").strip()
        
        publish_date_str = entry.find("atom:published", namespace).text
        publish_date = None
        if publish_date_str:
            try:
                publish_date = datetime.strptime(publish_date_str, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                pass
                
        authors = ", ".join([author.find("atom:name", namespace).text for author in entry.findall("atom:author", namespace)])
        
        pdf_url = None
        for link in entry.findall("atom:link", namespace):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href")
                break
                
        primary_category = None
        primary_category_elem = entry.find("arxiv:primary_category", namespace)
        if primary_category_elem is not None:
            primary_category = primary_category_elem.attrib.get("term")

        return RawArticleSchema(
            source=self.source_name,
            external_id=external_id,
            title=title,
            abstract_text=abstract_text,
            publish_date=publish_date,
            authors=authors,
            pdf_url=pdf_url,
            primary_category=primary_category
        )

    async def fetch_articles(self, query: str, max_results: int = 10) -> List[RawArticleSchema]:
        import calendar
        articles = []
        
        # State dosyasından kalınan yeri oku
        saved_state = load_state("arxiv")
        
        # Eski int formatından yeni dict formatına geçiş (Migration)
        if isinstance(saved_state, int) or isinstance(saved_state, str):
            current_date = "2000-01-01"
            current_start = 0
        elif isinstance(saved_state, dict):
            current_date = saved_state.get("current_date", "2000-01-01")
            current_start = saved_state.get("start_offset", 0)
        else:
            current_date = "2000-01-01"
            current_start = 0
            
        current_dt = datetime.strptime(current_date, "%Y-%m-%d")
        
        base_query = "cat:cs.*"
        if query.strip():
            encoded_query = urllib.parse.quote(query)
            base_query = f"all:{encoded_query}+AND+cat:cs.*"

        while len(articles) < max_results:
            year = current_dt.year
            month = current_dt.month
            
            # Bulunduğumuz ayın son gününü bul
            _, last_day = calendar.monthrange(year, month)
            
            # Tarih aralığını formatla: YYYYMMDDHHMM
            start_date_str = f"{year:04d}{month:02d}010000"
            end_date_str = f"{year:04d}{month:02d}{last_day:02d}2359"
            
            # Bu ay için ne kadar çekeceğiz
            chunk_size = min(500, max_results - len(articles))
            
            search_param = f"{base_query}+AND+submittedDate:[{start_date_str}+TO+{end_date_str}]"
            url = f"{self.BASE_URL}?search_query={search_param}&start={current_start}&max_results={chunk_size}&sortBy=submittedDate&sortOrder=ascending"
            
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers={"User-Agent": "Academic Literature Platform/1.0"}) as client:
                response = await client.get(url)
                if response.status_code == 429:
                    import asyncio
                    await asyncio.sleep(10) # Rate limit: ArXiv bizi bir süreliğine engelledi, 10 saniye bekle
                    continue
                elif response.status_code != 200:
                    import asyncio
                    await asyncio.sleep(5)
                    continue

            namespace = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom"
            }
            root = ET.fromstring(response.text)
            entries = root.findall("atom:entry", namespace)
            
            # Eğer bu aya ait makale kalmadıysa, sonraki aya geç
            if not entries:
                if month == 12:
                    current_dt = datetime(year + 1, 1, 1)
                else:
                    current_dt = datetime(year, month + 1, 1)
                
                # Gelecekteki bir tarihe ulaştıysak durdur
                if current_dt > datetime.now():
                    break
                    
                current_start = 0
                
                # Ay değiştiği için State'i sıfırlayarak güncelle
                save_state("arxiv", {
                    "current_date": current_dt.strftime("%Y-%m-%d"),
                    "start_offset": current_start
                })
                
                # Ay geçişlerinde de rate limit'e takılmamak için bekle
                import asyncio
                await asyncio.sleep(3)
                continue
                
            for entry in entries:
                articles.append(self._parse_entry(entry, namespace))
                
            current_start += chunk_size
            
            # Kaydetme işlemi başarılı olduysa state'i güncelle
            save_state("arxiv", {
                "current_date": current_dt.strftime("%Y-%m-%d"),
                "start_offset": current_start
            })
                
            import asyncio
            await asyncio.sleep(3.5) # ArXiv API kuralları gereği her istek arası en az 3 saniye bekle
            
        return articles

    async def fetch_article_by_id(self, article_id: str) -> Optional[RawArticleSchema]:
        url = f"{self.BASE_URL}?id_list={article_id}"
        
        async with httpx.AsyncClient(follow_redirects=True, headers={"User-Agent": "Academic Literature Platform/1.0"}) as client:
            response = await client.get(url)
            response.raise_for_status()

        namespace = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom"
        }
        root = ET.fromstring(response.text)
        entries = root.findall("atom:entry", namespace)
        
        if not entries:
            return None
            
        return self._parse_entry(entries[0], namespace)
