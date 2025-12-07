from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import build_datasets
from .recommender import recommend_for_user
from .llm_explainer import generate_explanation
from .models import Product, Recommendation, RecommendationsResponse, User

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Recommender API",
    description="Recommends products and explains why they are recommended.",
    version="1.0.0",
)

# Allow frontend (Streamlit) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load datasets once when the server starts
users_df, products_df, interactions_df = build_datasets()


@app.get("/users", response_model=list[User])
def list_users():
    """Return a list of users (for frontend dropdown/demo)."""
    users = []
    for _, row in users_df.iterrows():
        users.append(
            User(
                user_id=int(row["user_id"]),
                name=row["name"],
            )
        )
    return users


@app.get("/products", response_model=list[Product])
def list_products():
    """Return all products (for debugging/demo)."""
    products = []
    for _, row in products_df.iterrows():
        products.append(
            Product(
                product_id=int(row["product_id"]),
                name=row["name"],
                category=row["category"],
                brand=row["brand"],
                price=float(row["price"]),
                tags=str(row.get("tags", "")),
            )
        )
    return products


@app.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(user_id: int, top_k: int = 5):
    
    # Validate user exists
    user_row = users_df[users_df["user_id"] == user_id]
    if user_row.empty:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # 1. Get recommendations from recommender
    recs = recommend_for_user(user_id=user_id, top_k=top_k)

    # 2. For each recommended product, generate explanation
    api_recommendations: list[Recommendation] = []
    for r in recs:
        explanation = generate_explanation(user_id=user_id, product=r)

        prod = Product(
            product_id=r["product_id"],
            name=r["name"],
            category=r["category"],
            brand=r["brand"],
            price=r["price"],
            tags=r.get("tags", ""),
        )

        api_recommendations.append(
            Recommendation(
                product=prod,
                score=r["score"],
                explanation=explanation,
            )
        )

    return RecommendationsResponse(user_id=user_id, recommendations=api_recommendations)
