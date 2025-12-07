from pydantic import BaseModel
from typing import List, Optional


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    brand: str
    price: float
    tags: Optional[str] = None


class Recommendation(BaseModel):
    product: Product
    score: float
    explanation: str


class RecommendationsResponse(BaseModel):
    user_id: int
    recommendations: List[Recommendation]


class User(BaseModel):
    user_id: int
    name: str
