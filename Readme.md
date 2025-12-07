# 🛒 E-commerce Product Recommender with Explanations

This project is a simple end-to-end **product recommendation system for an e-commerce platform**.
It suggests products to users based on their previous activity and also explains *why* each product is being recommended using natural-language style explanations.

The main goal of this project is to combine:

* A **working recommendation engine**
* With **LLM-style human-readable explanations**
* And show everything in a **live web dashboard**

---

## 📌 Project Objective

To build a system that:

* Takes **product data + user interaction data**
* Generates **personalized product recommendations**
* Provides a **clear explanation for each recommendation**
* Displays the output in a simple **frontend dashboard**

---
## ✅ Output

<div style="display: flex; justify-content: center; margin-top: 10px;">

  <div style="border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px 20px;
    max-width: 900px;
    background: #fafafa;
    box-shadow: 0 4px 10px rgba(0,0,0,0.04);
  ">

  <p align="center" style="margin-bottom: 12px; font-weight: 600;">
    Sample Output – Product Recommendations with Explanations
  </p>

  <p align="center" style="margin: 0;">
    <img 
      src="assets/output.jpg" 
      alt="Project Output" 
      style="max-width: 100%; border-radius: 8px;"
    />
  </p>

  </div>

</div>

## 🧠 How the Recommendation Works

This project uses a **content-based recommendation approach** with user behavior weighting.

### 1. User Behavior Tracking

Each user interaction is assigned a weight:

* View → 1
* Click → 2
* Add to Cart → 3
* Purchase → 5

These weights help measure how interested a user was in a product.

### 2. Product Representation

Each product is converted into a text representation using:

* Product name
* Category
* Brand
* Tags

This text is transformed into numerical vectors using **TF-IDF**.

### 3. User Profile Creation

For each user:

* All interacted products are collected.
* Their TF-IDF vectors are combined using interaction weights.
* This forms a **user interest profile vector**.

### 4. Similarity Matching

* Cosine similarity is calculated between the user profile and all products.
* Products with higher similarity are ranked higher.

### 5. Popularity Boost

Final ranking uses a hybrid score:

```
Final Score = 70% Similarity + 30% Popularity
```

### 6. Cold Start Handling

If a user has no history, the system shows **popular products** instead.

---

## 🧾 Explanation Generation (LLM-Style)

For every recommended product, the system generates a **human-friendly explanation** based on:

* User’s recent activity
* Product category
* Brand preference
* Product tags

Even though a real LLM API is not mandatory, the explanation module is designed so it can be easily connected to **OpenAI or any other LLM in the future**.

Example explanation:

> “This product is recommended because it matches your interest in running shoes and you have previously interacted with similar sports products.”

---

## 🧩 System Architecture

```
[ CSV Data ]
      ↓
[ Recommendation Engine (TF-IDF + Cosine Similarity) ]
      ↓
[ Explanation Generator ]
      ↓
[ FastAPI Backend ]
      ↓
[ Streamlit Frontend Dashboard ]
```

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** Streamlit
* **Machine Learning:** Scikit-learn (TF-IDF, Cosine Similarity)
* **Data Handling:** Pandas, NumPy
* **Data Storage:** CSV files

---

## 📁 Project Structure

```
ecommerce-recommender/
├── backend/
│   ├── main.py
│   ├── db.py
│   ├── recommender.py
│   ├── llm_explainer.py
│   ├── models.py
│   └── __init__.py
├── frontend/
│   └── app.py
├── data/
│   ├── products.csv
│   ├── users.csv
│   └── interactions.csv
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run the Project

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Start the Backend (FastAPI)

From the **project root**:

```bash
uvicorn backend.main:app --reload
```

Open the API docs in browser:

```
http://127.0.0.1:8000/docs
```

---

### 3. Start the Frontend (Streamlit)

Open a new terminal:

```bash
streamlit run frontend/app.py
```

The app will open at:

```
http://localhost:8501
```

---

## ✅ API Endpoints

* `GET /users` → Fetch all users
* `GET /products` → Fetch all products
* `GET /recommendations?user_id=1&top_k=5` → Get recommendations with explanations

---

## 👨‍💻 Author - S Patel

Developed as part of an academic assignment project to demonstrate:

* Recommendation systems
* Backend API development
* ML integration
* LLM-style explanation generation
* Frontend dashboard visualization
