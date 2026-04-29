from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class RawArticleSchema(BaseModel):
    """
    Standardized schema for an article extracted from any API source.
    This schema directly maps to the `Article` SQLAlchemy model.
    """
    source: str = Field(..., description="Source of the article (e.g., 'arxiv', 'openalex', 'semanticscholar')")
    external_id: str = Field(..., description="Unique ID from the source")
    title: str = Field(..., description="Title of the article")
    abstract_text: Optional[str] = Field(None, description="Abstract of the article")
    publish_date: Optional[datetime] = Field(None, description="Publication date")
    authors: Optional[str] = Field(None, description="Comma-separated list of authors")
    pdf_url: Optional[str] = Field(None, description="URL to the PDF file")
    primary_category: Optional[str] = Field(None, description="Primary category or topic")

    def to_dict(self) -> dict:
        """Helper to convert to a dictionary suitable for SQLAlchemy ingestion."""
        # Convert HttpUrl to string if present (pydantic v2 handles this differently, but safe fallback)
        data = self.model_dump()
        return data
