from abc import ABC, abstractmethod
from typing import List, Optional
from ..schemas import RawArticleSchema

class BaseExtractor(ABC):
    """
    Abstract base class for all literature extractors.
    """

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Returns the identifier for this source (e.g., 'arxiv')"""
        pass

    @abstractmethod
    async def fetch_articles(self, query: str, max_results: int = 10) -> List[RawArticleSchema]:
        """
        Fetches articles based on a search query.
        
        Args:
            query (str): The search query.
            max_results (int): Maximum number of results to return.

        Returns:
            List[RawArticleSchema]: A list of standardized article schemas.
        """
        pass

    @abstractmethod
    async def fetch_article_by_id(self, article_id: str) -> Optional[RawArticleSchema]:
        """
        Fetches a single article by its unique external ID.
        
        Args:
            article_id (str): The ID of the article in the source system.

        Returns:
            Optional[RawArticleSchema]: The standardized article schema, or None if not found.
        """
        pass
