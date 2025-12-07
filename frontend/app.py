import requests
import streamlit as st

# ====== CONFIG ======
BACKEND_URL = "http://127.0.0.1:8000"


# ====== API HELPERS ======

def fetch_users():
    try:
        resp = requests.get(f"{BACKEND_URL}/users", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error fetching users: {e}")
        return []


def fetch_recommendations(user_id: int, top_k: int = 5):
    try:
        params = {"user_id": user_id, "top_k": top_k}
        resp = requests.get(f"{BACKEND_URL}/recommendations", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Error fetching recommendations: {e}")
        return None


# ====== STREAMLIT UI ======

def main():
    st.set_page_config(
        page_title="E-commerce Recommender",
        page_icon="🛒",
        layout="wide",
    )

    # ---- Global styling (subtle) ----
    st.markdown(
        """
        <style>
        /* Make the main area a bit softer */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Header Section ----
    left, right = st.columns([3, 2])

    with left:
        st.title("🛒 E-commerce Product Recommender")
        st.markdown(
            """
            This demo shows **personalized product recommendations** with  
            natural-language **explanations** for each suggestion.
            """
        )

        st.markdown(
            """
            ✅ Uses past interactions to find similar products  
            ✅ Ranks items by relevance score  
            ✅ Explains *why* each product was picked
            """
        )

    with right:
        with st.container(border=True):
            st.markdown("#### ℹ️ How to use")
            st.markdown(
                """
                1. Pick a user from the sidebar  
                2. Choose how many recommendations you want  
                3. Click **Get Recommendations**  
                4. Scroll through the cards and read the explanations
                """
            )

    st.markdown("---")

    # Sidebar controls
    st.sidebar.header("⚙️ Settings")

    # Load users for dropdown
    users = fetch_users()
    if not users:
        st.warning("No users loaded. Please check the backend.")
        return

    user_options = {f"{u['name']}": u["user_id"] for u in users}
    selected_label = st.sidebar.selectbox(
        "Select a user profile:",
        options=list(user_options.keys()),
    )
    selected_user_id = user_options[selected_label]

    top_k = st.sidebar.slider(
        "Number of recommendations",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
    )

    st.sidebar.markdown("---")

    # Main button
    if st.sidebar.button("🚀 Get Recommendations"):
        with st.spinner("Fetching recommendations..."):
            rec_data = fetch_recommendations(selected_user_id, top_k=top_k)

        if rec_data is None:
            return

        recs = rec_data.get("recommendations", [])

        st.subheader(f"🎯 Recommendations for **{selected_label}**")

        if not recs:
            st.info("No recommendations available for this user.")
            return

        st.caption(
            "Each card below shows the product details, relevance score, "
            "and a natural language explanation of why it was recommended."
        )

        # Display each recommendation as a card
        for idx, rec in enumerate(recs, start=1):
            product = rec["product"]
            score = rec["score"]
            explanation = rec["explanation"]

            # Keep score in [0, 1] range for progress bar
            try:
                normalized_score = max(0.0, min(float(score), 1.0))
            except Exception:
                normalized_score = 0.0

            with st.container(border=True):
                # Small label at top
                st.markdown(f"**#{idx} Recommended Product**")

                col1, col2 = st.columns([2, 3])

                with col1:
                    st.markdown(f"### 🛍️ {product['name']}")
                    st.markdown(
                        f"""
                        **Category:** `{product['category']}`  
                        **Brand:** `{product['brand']}`  
                        **Price:** ₹{product['price']:.2f}
                        """
                    )

                    st.markdown("**Relevance score**")
                    st.progress(normalized_score)

                    st.caption(f"Raw score: `{score:.3f}`")

                with col2:
                    st.markdown("**Why this product?**")
                    st.write(explanation)

    else:
        st.info("Select a user and click **Get Recommendations** from the sidebar to see results.")


if __name__ == "__main__":
    main()
