from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------- SINGLE RESPONSE ----------------
def rag_diet_reasoning(caption, nutrition):

    prompt = f"""
    You are a professional nutritionist AI.

    Food detected: {caption}

    Nutrition:
    Calories: {nutrition['calories']}
    Protein: {nutrition['protein']}
    Carbs: {nutrition['carbs']}
    Fat: {nutrition['fat']}

    Give:
    1. Health impact
    2. Diet advice
    3. Better alternative meal

    Keep it short, structured, and practical.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # 🔥 Best model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


# ---------------- WEEKLY ANALYSIS ----------------
def weekly_diet_recommendation(df):

    summary = df.describe().to_string()

    prompt = f"""
    Analyze this weekly nutrition data:

    {summary}

    Give:
    - Overall diet assessment
    - Improvements
    - Health suggestions
    Keep it short, structured, and practical.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content