import os
import faiss
import pickle
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# =========================
# Paths
# =========================
BASE = os.path.dirname(os.path.abspath(__file__))

index_path = os.path.join(BASE, "fndds_rag.faiss")
docs_path = os.path.join(BASE, "fndds_docs.pkl")

if not os.path.exists(index_path):
    raise Exception("RAG index not found. Run build_rag_db.py first.")

if not os.path.exists(docs_path):
    raise Exception("RAG documents not found. Run build_rag_db.py first.")

# =========================
# Load Model + Index
# =========================
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index(index_path)

with open(docs_path, "rb") as f:
    docs = pickle.load(f)

# =========================
# Parse nutrition document
# =========================
def parse_doc(doc):

    import re

    food = re.search(r"Food:\s*(.*)", doc).group(1)
    calories = float(re.search(r"Calories:\s*(.*)", doc).group(1))
    protein = float(re.search(r"Protein:\s*(.*)", doc).group(1))
    carbs = float(re.search(r"Carbs:\s*(.*)", doc).group(1))
    fat = float(re.search(r"Fat:\s*(.*)", doc).group(1))

    portion_match = re.search(r"Portion:\s*(.*)", doc)

    portion = float(portion_match.group(1)) if portion_match else 100

    return {
        "food_name": food,
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "portion": portion
    }
# =========================
# RAG Retrieval Function
# =========================
def retrieve_food_docs(query, k=3):

    emb = embed_model.encode([query])
    D, I = index.search(np.array(emb).astype("float32"), k)

    results = [parse_doc(docs[i]) for i in I[0]]

    # Nutrition fusion (average)
    fused = {
        "food_name": " + ".join([r["food_name"] for r in results]),
        "calories": round(float(np.mean([r["calories"] for r in results])), 2),
        "protein": round(float(np.mean([r["protein"] for r in results])), 2),
        "carbs": round(float(np.mean([r["carbs"] for r in results])), 2),
        "fat": round(float(np.mean([r["fat"] for r in results])), 2),
        "portion": round(float(np.mean([r["portion"] for r in results])), 2)
    }

    return fused