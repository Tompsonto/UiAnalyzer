"""
Database models for ClarityCheck analysis data
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2000), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    
    # Scores
    overall_score = Column(Float, nullable=False)
    visual_score = Column(Float, nullable=False)
    text_score = Column(Float, nullable=False)
    grade = Column(String(1), nullable=False)
    
    # Analysis data
    visual_analysis = Column(JSON, nullable=True)
    text_analysis = Column(JSON, nullable=True)
    issues = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Metadata
    title = Column(String(500), nullable=True)
    meta_description = Column(Text, nullable=True)
    screenshot_url = Column(String(1000), nullable=True)
    
    # Status
    status = Column(String(20), default="completed")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'domain': self.domain,
            'overall_score': self.overall_score,
            'visual_score': self.visual_score,
            'text_score': self.text_score,
            'grade': self.grade,
            'visual_analysis': self.visual_analysis,
            'text_analysis': self.text_analysis,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'title': self.title,
            'meta_description': self.meta_description,
            'screenshot_url': self.screenshot_url,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    
    # Plan information
    plan = Column(String(20), default="free")  # free, pro, agency, enterprise
    analyses_used = Column(Integer, default=0)
    analyses_limit = Column(Integer, default=3)  # Monthly limit
    
    # Subscription
    stripe_customer_id = Column(String(255), nullable=True)
    subscription_status = Column(String(20), default="inactive")
    subscription_end = Column(DateTime(timezone=True), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'plan': self.plan,
            'analyses_used': self.analyses_used,
            'analyses_limit': self.analyses_limit,
            'subscription_status': self.subscription_status,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_login': self.last_login
        }

class AnalysisCache(Base):
    __tablename__ = "analysis_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    cached_data = Column(JSON, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at