from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from .database_session import Base



class RequestLog(Base):
    __tablename__ = "requests_log"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(Text, nullable=False)
    country_code = Column(Text, nullable=True)
    ip_address = Column(Text, nullable=False)
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)
    user_country = Column(Text, nullable=True)
    user_city = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    response_status = Column(Integer, nullable=True)
    request_id = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())





