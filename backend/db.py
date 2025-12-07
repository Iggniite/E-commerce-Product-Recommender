import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Weights for different interaction types
EVENT_WEIGHTS = {
    "view": 1,
    "click": 2,
    "add_to_cart": 3,
    "purchase": 5,
}

#  Load products from CSV
def load_products() -> pd.DataFrame:
    products_path = DATA_DIR / "products.csv"
    products = pd.read_csv(products_path)
    return products

#Load users from CSV
def load_users() -> pd.DataFrame:
    users_path = DATA_DIR / "users.csv"
    users = pd.read_csv(users_path)
    return users

# Load interactions from CSV and optionally add a numeric weight column
def load_interactions(add_weights: bool = True) -> pd.DataFrame:
    interactions_path = DATA_DIR / "interactions.csv"
    interactions = pd.read_csv(interactions_path)

    if add_weights:
        interactions["weight"] = interactions["event_type"].map(EVENT_WEIGHTS).fillna(0)

    return interactions


def build_datasets():
    users = load_users()
    products = load_products()
    interactions = load_interactions(add_weights=True)

    # Compute product popularity = sum of weights per product
    popularity = (
        interactions.groupby("product_id")["weight"]
        .sum()
        .rename("popularity")
        .reset_index()
    )

    # Merge popularity into products dataframe
    products = products.merge(popularity, on="product_id", how="left")
    products["popularity"] = products["popularity"].fillna(0)

    return users, products, interactions
