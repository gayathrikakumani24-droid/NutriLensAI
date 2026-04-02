import pandas as pd
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

df = pd.read_csv("fndds.xlsx")

documents = []
texts = []

for _, row in df.iterrows():

    text = f"""
    Food: {row['food_description']}
    Calories: {row['energy_kcal']}
    Protein: {row['protein_g']}
    Carbs: {row['carbs_g']}
    Fat: {row['fat_g']}
    Portion: {row['gram_weight']}
    """

    documents.append(text)
    texts.append(row["food_description"])

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(texts)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings).astype("float32"))

faiss.write_index(index, "fndds_rag.faiss")

with open("fndds_docs.pkl", "wb") as f:
    pickle.dump(documents, f)

print("RAG DB built successfully")