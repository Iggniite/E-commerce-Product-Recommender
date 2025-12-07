from __future__ import annotations

from typing import Dict, List

from .recommender import users_df, products_df, interactions_df


def _get_user_past_products(user_id: int, limit: int = 5) -> List[Dict]:
    user_events = interactions_df[interactions_df["user_id"] == user_id]

    if user_events.empty:
        return []

    # Sort by timestamp descending to get recent ones
    user_events = user_events.sort_values("timestamp", ascending=False)

    recent = user_events.merge(
        products_df, on="product_id", how="left"
    ).head(limit)

    result = []
    for _, row in recent.iterrows():
        result.append(
            {
                "product_id": int(row["product_id"]),
                "name": row["name"],
                "category": row["category"],
                "brand": row["brand"],
                "event_type": row["event_type"],
            }
        )
    return result


def build_user_behavior_summary(user_id: int) -> str:
    user_row = users_df[users_df["user_id"] == user_id]
    if user_row.empty:
        user_name = f"User {user_id}"
    else:
        user_name = user_row.iloc[0]["name"]

    recent_products = _get_user_past_products(user_id, limit=5)
    if not recent_products:
        return f"{user_name} is a new user with no previous activity."

    parts = [f"{user_name} recently interacted with these products:"]

    for p in recent_products:
        parts.append(
            f"- {p['name']} ({p['category']}, {p['brand']}) via {p['event_type']}"
        )

    return "\n".join(parts)


def generate_explanation(user_id: int, product: Dict) -> str:
    user_summary = build_user_behavior_summary(user_id)

    prod_name = product.get("name", "this product")
    category = product.get("category", "")
    brand = product.get("brand", "")
    tags = product.get("tags", "") or ""

    # Basic heuristics for explanation
    explanation_parts = []

    if "new user with no previous activity" in user_summary:
        # Cold start explanation
        explanation_parts.append(
            f"We recommend **{prod_name}** because it is a popular {category.lower()} from {brand} "
            f"and well suited for many users."
        )
    else:
        explanation_parts.append(
            f"**{prod_name}** is recommended because it matches your interest in {category.lower()} products."
        )

        # Check if brand appeared before
        user_events = interactions_df[interactions_df["user_id"] == user_id]
        merged = user_events.merge(products_df, on="product_id", how="left")

        past_brands = set(merged["brand"].dropna().tolist())
        past_categories = set(merged["category"].dropna().tolist())

        if brand in past_brands:
            explanation_parts.append(
                f"You have previously interacted with products from **{brand}**, so this should feel familiar."
            )

        if category in past_categories:
            explanation_parts.append(
                f"You’ve shown interest in **{category.lower()}** before, and this item fits that preference."
            )

        # Use tags if informative
        if isinstance(tags, str) and tags.strip():
            main_tags = ", ".join(tags.split()[:3])
            explanation_parts.append(
                f"It is designed for **{main_tags}**, which aligns with your recent browsing activity."
            )

    # Add a more natural closing sentence
    explanation_parts.append(
        "Overall, this product aligns well with your recent activity and preferences."
    )

    return " ".join(explanation_parts)
