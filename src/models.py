"""
SQLAlchemy model for the nodes table.

Table: nodes
- id: SERIAL PRIMARY KEY
- name: VARCHAR UNIQUE NOT NULL
- host: VARCHAR NOT NULL
- port: INTEGER NOT NULL
- status: VARCHAR DEFAULT 'active'
- created_at: TIMESTAMP DEFAULT NOW()
- updated_at: TIMESTAMP DEFAULT NOW()
"""

# TODO: Implement your SQLAlchemy model here
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Node(Base):
    __tablename__ = "nodes"

    # SERIAL PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)
    
    # VARCHAR UNIQUE, NOT NULL
    name = Column(String, unique=True, index=True, nullable=False)
    
    # VARCHAR NOT NULL
    host = Column(String, nullable=False)
    
    # INTEGER NOT NULL
    port = Column(Integer, nullable=False)
    
    # VARCHAR DEFAULT 'active'
    status = Column(String, server_default="active", default="active", nullable=False)
    
    # TIMESTAMP DEFAULT NOW()
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # TIMESTAMP DEFAULT NOW() (with auto-update on changes)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())