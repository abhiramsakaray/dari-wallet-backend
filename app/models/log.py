from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Log(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG
    category = Column(String, nullable=False)  # auth, wallet, transaction, admin, system
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured data
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))  # Null for system logs
    
    # Relationships
    user = relationship("User", back_populates="logs")
    
    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', category='{self.category}')>" 