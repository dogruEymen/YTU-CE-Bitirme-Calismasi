from sqlalchemy import Column, Integer, ForeignKey
from datetime import datetime
from database.db import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
