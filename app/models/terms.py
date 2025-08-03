from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class TermsStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class TermsAndConditions(Base):
    __tablename__ = "terms_and_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(TermsStatus), default=TermsStatus.DRAFT)
    is_current = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    user_agreements = relationship("UserTermsAgreement", back_populates="terms")
    
    def __repr__(self):
        return f"<TermsAndConditions(id={self.id}, version='{self.version}', status='{self.status.value}')>"


class UserTermsAgreement(Base):
    __tablename__ = "user_terms_agreements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    terms_id = Column(Integer, ForeignKey("terms_and_conditions.id"), nullable=False)
    ip_address = Column(String)
    user_agent = Column(String)
    accepted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="terms_agreements")
    terms = relationship("TermsAndConditions", back_populates="user_agreements")
    
    def __repr__(self):
        return f"<UserTermsAgreement(user_id={self.user_id}, terms_id={self.terms_id}, accepted_at={self.accepted_at})>" 