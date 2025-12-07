from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .db import build_datasets

# Load data once when module is imported
users_df, products_df, interactions_df = build_datasets()


def _build_product_corpus(products):
    """
    Combine product fields into a single text string per product
    for TF-IDF.
    """
    name = products["name"].fillna("")
    category = products["category"].fillna("")
    brand = products["brand"].fillna("")
    tags = products["tags"].fillna("")

    corpus = name + " " + category + " " + brand + " " + tags
    return corpus


# Prepare TF-IDF model for all products
_product_corpus = _build_product_corpus(products_df)
_vectorizer = TfidfVectorizer()
_product_tfidf = _vectorizer.fit_transform(_product_corpus)

# Map product_id -> row index in TF-IDF matrix
_product_id_to_index = {
    int(pid): idx for idx, pid in enumerate(products_df["product_id"].tolist())
}


def _build_user_profile(user_id: int):
    """
    Build a TF-IDF user profile vector as a weighted average
    of the products they interacted with.
    """
    user_events = interactions_df[interactions_df["user_id"] == user_id]

    if user_events.empty:
        # No history for this user
        return None

    # Aggregate weights by product (some users interact multiple times)
    aggregated = (
        user_events.groupby("product_id")["weight"]
        .sum()
        .reset_index()
    )

    vectors = []
    weights = []

    for _, row in aggregated.iterrows():
        pid = int(row["product_id"])
        w = float(row["weight"])
        idx = _product_id_to_index.get(pid)

        if idx is None:
            continue

        vectors.append(_product_tfidf[idx].toarray()[0])
        weights.append(w)

    if not vectors:
        return None

    vectors = np.array(vectors)
    weights = np.array(weights).reshape(-1, 1)

    # Weighted average of product vectors
    profile = (vectors * weights).sum(axis=0) / weights.sum()
    return profile.reshape(1, -1) 


def recommend_for_user(user_id: int, top_k: int = 5):
    """
    Return a list of recommended products for a given user.
    Each item is a dict with product fields + score.
    """
    profile = _build_user_profile(user_id)

    # Cold-start: no profile -> recommend by popularity only
    if profile is None:
        cold_df = products_df.copy()
        max_pop = cold_df["popularity"].max() or 1
        cold_df["pop_norm"] = cold_df["popularity"] / max_pop
        cold_df["final_score"] = cold_df["pop_norm"]

        ranked = cold_df.sort_values("final_score", ascending=False).head(top_k)

        return [
            {
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "tags": row.get("tags", ""),
                "score": float(row["final_score"]),
            }
            for _, row in ranked.iterrows()
        ]

    # Normal case: we have a user profile
    # 1. Cosine similarity between user profile and all product vectors
    sims = cosine_similarity(profile, _product_tfidf)[0]

    rec_df = products_df.copy()
    rec_df["similarity"] = sims

    # 2. Optionally exclude products the user already purchased
    purchased_ids = set(
        interactions_df[
            (interactions_df["user_id"] == user_id)
            & (interactions_df["event_type"] == "purchase")
        ]["product_id"].tolist()
    )
    if purchased_ids:
        rec_df = rec_df[~rec_df["product_id"].isin(purchased_ids)]

    # 3. Add normalized popularity
    max_pop = rec_df["popularity"].max() or 1
    rec_df["pop_norm"] = rec_df["popularity"] / max_pop

    # 4. Hybrid score: 70% similarity + 30% popularity
    rec_df["final_score"] = 0.7 * rec_df["similarity"] + 0.3 * rec_df["pop_norm"]

    # 5. Sort and take top_k
    ranked = rec_df.sort_values("final_score", ascending=False).head(top_k)

    recommendations = []
    for _, row in ranked.iterrows():
        recommendations.append(
            {
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "brand": row["brand"],
                "price": float(row["price"]),
                "tags": row.get("tags", ""),
                "score": float(row["final_score"]),
            }
        )

    return recommendations
