from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, CheckConstraint
from datetime import datetime

from database.db import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id      = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role    = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    __tableargs__ = (
        CheckConstraint("role IN ('user', 'agent')")
    )
