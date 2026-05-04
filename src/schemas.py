"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

# TODO: Implement your Pydantic schemas here
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class NodeBase(BaseModel):
    """
    Base schema with shared attributes.
    """
    name: str = Field(..., description="Unique name of the node")
    host: str = Field(..., min_length=1, description="IP address or hostname")
    port: int = Field(..., ge=1, le=65535, description="Port number (1-65535)")

class NodeCreate(NodeBase):
    """
    Schema for POST /api/nodes.
    All fields from NodeBase are required here.
    """
    pass

class NodeUpdate(BaseModel):
    """
    Schema for PUT /api/nodes/{name}.
    Fields are optional for partial updates.
    """
    host: Optional[str] = Field(None, min_length=1)
    port: Optional[int] = Field(None, ge=1, le=65535)

class NodeResponse(NodeBase):
    """
    Schema for API responses.
    Includes database-generated fields.
    """
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    # This allows Pydantic to read data from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)