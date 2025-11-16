"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Example schemas (you can keep these or remove if not needed)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Affiliate funnel schemas

class Lead(BaseModel):
    """
    Captured lead from opt-in form
    Collection: "lead"
    """
    name: str = Field(..., description="Lead name")
    email: EmailStr = Field(..., description="Lead email")
    source: Optional[str] = Field("landing", description="Traffic source or campaign tag")

class Offer(BaseModel):
    """
    Affiliate offer configuration
    Collection: "offer"
    """
    slug: str = Field(..., description="Short identifier used in redirect URL")
    title: str = Field(..., description="Offer title")
    url: str = Field(..., description="Destination affiliate URL")
    description: Optional[str] = Field(None, description="Short description shown on thank-you page")
    active: bool = Field(True, description="Whether offer is active")

class Click(BaseModel):
    """
    Click tracking for redirects
    Collection: "click"
    """
    slug: str = Field(..., description="Offer slug clicked")
    lead_id: Optional[str] = Field(None, description="Associated lead id, if any")
    ip: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="Browser user agent")
