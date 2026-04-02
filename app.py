import streamlit as st
from PIL import Image
import datetime
import pandas as pd
import plotly.express as px

from blip_model import generate_caption
from rag_retriever import retrieve_food_docs
from recommender import rag_diet_reasoning, weekly_diet_recommendation
from portion_estimator import estimate_portion
from database import SessionLocal, FoodHistory

st.set_page_config(page_title="NutriLens AI", layout="wide")

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "upload"

if "base_portion" not in st.session_state:
    st.session_state.base_portion = 100

if "nut" not in st.session_state:
    st.session_state.nut = {
        "food_name": "",
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "portion": 100
    }

if "caption" not in st.session_state:
    st.session_state.caption = ""

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# ---------------- CSS ----------------
st.markdown("""
<style>
html, body, .stApp {
    background: #0b0f14;
    color: white;
}

.navbar {
    padding: 15px;
    display:flex;
    justify-content:space-between;
}

.logo {
    font-size: 26px;
    font-weight: 800;
    background: linear-gradient(90deg,#ffffff,#9cff57,#5cff9c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.card {
    background:linear-gradient(135deg,#9cff57,#5cff9c);
    color:black;
    padding:20px;
    border-radius:20px;
}
.card:hover {
    background: linear-gradient(135deg,#9cff57,#5cff9c);
    color: black;
    box-shadow: 0 0 12px #9cff57;
    transform: translateY(-2px);
}
/* NAV BUTTONS */
/* 🔘 ALL STREAMLIT BUTTONS */
div[data-testid="stButton"] > button {
    border-radius: 12px;
    height: 40px;
    font-weight: 600;
    background: rgba(255,255,255,0.1);
    color: white;
    border: 1px solid rgba(255,255,255,0.15);
    transition: all 0.3s ease;
}

/* ✨ HOVER */
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg,#9cff57,#5cff9c);
    color: black;
    box-shadow: 0 0 12px #9cff57;
    transform: translateY(-2px);
}

/* 👇 CLICK */
div[data-testid="stButton"] > button:active {
    background: linear-gradient(135deg,#9cff57,#5cff9c);
    color: black;
    box-shadow: 0 0 12px #9cff57;
    
}
.neon-loader {
  border: 4px solid rgba(156,255,87,0.1);
  border-top: 4px solid #9cff57;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  margin: auto;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 15px #9cff57;
}

@keyframes spin {
  0% { transform: rotate(0deg);}
  100% { transform: rotate(360deg);}
}

[data-testid="stMetric"]:hover {
    box-shadow:0 0 20px #9cff57;
}
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
upload_active = "active" if st.session_state.page == "upload" else ""
analytics_active = "active" if st.session_state.page == "analytics" else ""

st.markdown('<div class="navbar">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([4,1,1])
with col1:
    st.markdown('<div class="logo">🍽️ NutriLens AI</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="nav-btn {upload_active}">', unsafe_allow_html=True)
    if st.button("📤 Upload"):
        st.session_state.page = "upload"
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="nav-btn {analytics_active}">', unsafe_allow_html=True)
    if st.button("📊 Analytics"):
        st.session_state.page = "analytics"
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======================================================
# 📤 UPLOAD PAGE
# ======================================================
if st.session_state.page == "upload":

    st.subheader("Upload & Analyze Meal")

    file = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])

    if file:
        image = Image.open(file).convert("RGB")

        col1, col2 = st.columns([1,1])

        with col1:
            st.image(image, width="stretch")

        # 🔥 ANALYZE BUTTON
        if st.button("🚀 Analyze Meal"):

            with col2:
                placeholder = st.empty()

                # Loader
                with placeholder:
                    st.markdown("""
                    <div style="text-align:center; padding-top:120px;">
                        <div class="neon-loader"></div>
                        <p style="color:#aaa;">Analyzing your meal...</p>
                    </div>
                    """, unsafe_allow_html=True)

                # AI Processing
                caption = generate_caption(image)
                nut = retrieve_food_docs(caption)
                portion = estimate_portion(image)

                # Save to session
                st.session_state.caption = caption
                st.session_state.nut = nut
                st.session_state.base_portion = portion
                st.session_state.analysis_done = True

                placeholder.empty()

        # 🔥 SHOW RESULTS AFTER ANALYSIS
        if st.session_state.analysis_done:

            with col2:

                st.markdown(f"""
                <div style="background:rgba(156,255,87,0.1);
                padding:10px;border-radius:10px;color:#9cff57;">
                ✔ Detected: {st.session_state.caption}
                </div>
                """, unsafe_allow_html=True)

                # 🎯 SLIDER
                user_portion = st.slider(
                    "Adjust Portion (grams)",
                    50, 500,
                    int(st.session_state.base_portion),
                    step=10
                )

                scale = user_portion / st.session_state.nut.get("portion", 100)

                nut_scaled = {
                    "calories": round(st.session_state.nut["calories"] * scale, 2),
                    "protein": round(st.session_state.nut["protein"] * scale, 2),
                    "carbs": round(st.session_state.nut["carbs"] * scale, 2),
                    "fat": round(st.session_state.nut["fat"] * scale, 2),
                }

                st.info(f"Portion: {user_portion:.2f} g")

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Calories", nut_scaled["calories"])
                m2.metric("Protein", nut_scaled["protein"])
                m3.metric("Carbs", nut_scaled["carbs"])
                m4.metric("Fat", nut_scaled["fat"])

                # 🤖 AI DYNAMIC
                ai_rec = rag_diet_reasoning(
                    st.session_state.caption,
                    nut_scaled
                )

                st.markdown("### 🤖 AI Recommendation")
                st.markdown(f"""
                <div class="card">{ai_rec}</div>
                """, unsafe_allow_html=True)

            # SAVE
            db = SessionLocal()
            entry = FoodHistory(
                date=datetime.date.today(),
                food=st.session_state.nut["food_name"],
                calories=nut_scaled["calories"],
                protein=nut_scaled["protein"],
                carbs=nut_scaled["carbs"],
                fat=nut_scaled["fat"]
            )
            db.add(entry)
            db.commit()
            db.close()

# ======================================================
# 📊 ANALYTICS PAGE (UNCHANGED)
# ======================================================
elif st.session_state.page == "analytics":

    st.subheader("📊 Nutrition Dashboard")

    db = SessionLocal()
    data = db.query(FoodHistory).all()
    db.close()

    if len(data) == 0:
        st.warning("No data available")
    else:
        df = pd.DataFrame([{
            "date": d.date,
            "food": d.food,
            "calories": d.calories,
            "protein": d.protein,
            "carbs": d.carbs,
            "fat": d.fat
        } for d in data])

        df["date"] = pd.to_datetime(df["date"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", round(df["calories"].sum(),2))
        c2.metric("Protein", round(df["protein"].sum(),2))
        c3.metric("Carbs", round(df["carbs"].sum(),2))
        c4.metric("Fat", round(df["fat"].sum(),2))

        daily = df.groupby("date").sum().reset_index()
        st.plotly_chart(px.bar(daily, x="date", y="calories"))

        weekly = df.groupby(pd.Grouper(key="date", freq="W")).sum().reset_index()
        st.plotly_chart(px.line(weekly, x="date",
                                y=["calories","protein","carbs","fat"]))
        st.markdown("### 🥗 Macronutrient Distribution")

        totals = {
            "Protein": df["protein"].sum(),
            "Carbs": df["carbs"].sum(),
            "Fat": df["fat"].sum()
        }

        pie = px.pie(
            names=list(totals.keys()),
            values=list(totals.values()),
            title="Macro Distribution",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(pie, use_container_width=True)
        st.markdown("### 🔥 Calorie Trend (Smooth)")

        fig = px.line(
            daily,
            x="date",
            y="calories",
            line_shape="spline",
            title="Smooth Calorie Trend"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### ⚖️ Nutrition Comparison")
        latest = df.iloc[-1]
        compare_df = pd.DataFrame({
            "Nutrient": ["Calories", "Protein", "Carbs", "Fat"],
            "Value": [
                latest["calories"],
                latest["protein"],
                latest["carbs"],
                latest["fat"]
            ]
        })

        fig = px.bar(
            compare_df,
            x="Nutrient",
            y="Value",
            color="Value",
            color_continuous_scale="viridis",
            title="Latest Meal Nutrition"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### 🤖 Weekly AI Insights")
        st.info(weekly_diet_recommendation(weekly))