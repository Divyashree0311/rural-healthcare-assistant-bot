import streamlit as st
import pandas as pd
from pymongo import MongoClient

# -------------------------
# MongoDB connection
# -------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["rural_health_ai"]
collection = db.sessions

st.set_page_config(page_title="Rural Health Dashboard", layout="wide")
st.title("📊 Rural Health AI – Admin Dashboard")

# -------------------------
# Fetch data
# -------------------------
records = list(collection.find({}, {"_id": 0}))

if not records:
    st.warning("No records found in database.")
    st.stop()

df = pd.DataFrame(records)

# -------------------------
# BACKWARD COMPATIBILITY FIX
# -------------------------
REQUIRED_COLUMNS = [
    "phone_number",
    "name",
    "age",
    "category",
    "predicted_condition",
    "severity",
    "language",
    "advice",
    "timestamp",
    "answers"
]

for col in REQUIRED_COLUMNS:
    if col not in df.columns:
        df[col] = "N/A"

# -------------------------
# Sidebar filters
# -------------------------
st.sidebar.header("🔍 Filters")

category_filter = st.sidebar.multiselect(
    "Category",
    options=df["category"].unique(),
    default=list(df["category"].unique())
)

severity_filter = st.sidebar.multiselect(
    "Severity",
    options=df["severity"].unique(),
    default=list(df["severity"].unique())
)

df_filtered = df[
    (df["category"].isin(category_filter)) &
    (df["severity"].isin(severity_filter))
]

# -------------------------
# KPI Metrics
# -------------------------
c1, c2, c3 = st.columns(3)
c1.metric("Total Users", len(df_filtered))
c2.metric("Emergency Cases", len(df_filtered[df_filtered["severity"] == "emergency"]))
c3.metric("Languages Used", df_filtered["language"].nunique())

# -------------------------
# Table View
# -------------------------
st.subheader("📋 User Records")

display_columns = [
    "phone_number",
    "name",
    "age",
    "category",
    "predicted_condition",
    "severity",
    "language",
    "timestamp"
]

st.dataframe(
    df_filtered[display_columns],
    use_container_width=True
)

# -------------------------
# Detailed Case View
# -------------------------
st.subheader("🩺 Case Details")

selected_index = st.selectbox(
    "Select record index",
    df_filtered.index
)

selected = df_filtered.loc[selected_index]

st.json({
    "Phone Number": selected["phone_number"],
    "Name": selected["name"],
    "Age": selected["age"],
    "Category": selected["category"],
    "Detected Condition": selected["predicted_condition"],
    "Severity": selected["severity"],
    "Language": selected["language"],
    "Advice Sent": selected["advice"],
    "Symptoms (Answers)": selected["answers"],
    "Timestamp": str(selected["timestamp"])
})
