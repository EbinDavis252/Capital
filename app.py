import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI-Driven Capital Allocation Advisor", layout="wide")

st.title("💼 AI-Driven Capital Allocation Advisor")
st.markdown("### Decision Support System for Finance Leaders")

# Load data
df = pd.read_csv("projects_data.csv")

# Sidebar controls
st.sidebar.header("🔧 Assumptions")
discount_rate = st.sidebar.slider("Discount Rate (%)", 5, 20, 10) / 100
total_budget = st.sidebar.number_input("Total Capital Budget", value=10000000, step=500000)

scenario = st.sidebar.selectbox(
    "Scenario",
    ["Base Case", "Best Case", "Worst Case"]
)

# Scenario adjustments
scenario_multiplier = {
    "Base Case": 1.0,
    "Best Case": 1.15,
    "Worst Case": 0.85
}[scenario]

# Forecast cash flows
df["Adjusted_Revenue"] = df["Expected_Annual_Revenue"] * scenario_multiplier
df["Annual_Cash_Flow"] = df["Adjusted_Revenue"] - df["Annual_Cost"]

# NPV calculation
def calculate_npv(cash_flow, years, rate):
    return sum([cash_flow / ((1 + rate) ** t) for t in range(1, years + 1)])

df["NPV"] = df.apply(
    lambda x: calculate_npv(x["Annual_Cash_Flow"], x["Duration_Years"], discount_rate)
              - x["Initial_Investment"],
    axis=1
)

# Risk-adjusted NPV
df["Risk_Adjusted_NPV"] = df["NPV"] * (1 - df["Risk_Score"]) * df["Strategic_Weight"]

# Capital allocation logic
df = df.sort_values("Risk_Adjusted_NPV", ascending=False)

allocated_capital = 0
allocations = []

for _, row in df.iterrows():
    if allocated_capital + row["Initial_Investment"] <= total_budget:
        allocations.append("Approved")
        allocated_capital += row["Initial_Investment"]
    else:
        allocations.append("Rejected")

df["Allocation_Decision"] = allocations

# Dashboard layout
st.subheader("📊 Project Evaluation Summary")
st.dataframe(df.style.format({
    "NPV": "₹{:,.0f}",
    "Risk_Adjusted_NPV": "₹{:,.0f}",
    "Initial_Investment": "₹{:,.0f}",
    "Annual_Cash_Flow": "₹{:,.0f}"
}))

# KPIs
approved_projects = df[df["Allocation_Decision"] == "Approved"]

col1, col2, col3 = st.columns(3)
col1.metric("Total Budget", f"₹{total_budget:,.0f}")
col2.metric("Allocated Capital", f"₹{allocated_capital:,.0f}")
col3.metric("Portfolio NPV", f"₹{approved_projects['NPV'].sum():,.0f}")

# Charts
st.subheader("📈 Risk vs Return")
st.scatter_chart(
    df,
    x="Risk_Score",
    y="NPV",
    color="Allocation_Decision",
    size="Initial_Investment"
)

st.subheader("🏆 Capital Allocation Recommendation")
for _, row in approved_projects.iterrows():
    st.success(
        f"{row['Project']} approved | Investment: ₹{row['Initial_Investment']:,.0f} | "
        f"Risk-Adjusted NPV: ₹{row['Risk_Adjusted_NPV']:,.0f}"
    )

st.markdown("---")
st.markdown("📌 *This AI-driven advisor combines financial modeling, risk adjustment, and scenario analysis to support strategic capital allocation decisions.*")
