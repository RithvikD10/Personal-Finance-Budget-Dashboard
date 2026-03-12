from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from utils import (
    DataValidationError,
    category_expense_summary,
    expense_forecast,
    get_kpis,
    load_and_prepare_data,
    monthly_category_breakdown,
    monthly_summary,
    savings_goal_projection,
    top_expense_month,
)

st.set_page_config(page_title="Personal Finance Dashboard", page_icon="💸", layout="wide")


def currency(value: float) -> str:
    return f"${value:,.2f}"


def line_chart(monthly_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(monthly_df["month"], monthly_df["Income"], marker="o", label="Income")
    ax.plot(monthly_df["month"], monthly_df["Expense"], marker="o", label="Expenses")
    ax.plot(monthly_df["month"], monthly_df["Net"], marker="o", label="Net Cash Flow")
    ax.set_title("Monthly Financial Trends")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


def category_bar_chart(category_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(category_df["category"], category_df["amount"])
    ax.set_title("Expenses by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Total Expense")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def stacked_category_chart(breakdown_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    categories = [col for col in breakdown_df.columns if col != "month"]
    bottom = pd.Series([0] * len(breakdown_df))
    for category in categories:
        ax.bar(breakdown_df["month"], breakdown_df[category], bottom=bottom, label=category)
        bottom += breakdown_df[category]
    ax.set_title("Monthly Expense Mix")
    ax.set_xlabel("Month")
    ax.set_ylabel("Expense")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


def forecast_chart(monthly_df: pd.DataFrame, forecast_periods: list[str], forecast_values: list[float]):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(monthly_df["month"], monthly_df["Expense"], marker="o", label="Historical Expenses")
    ax.plot(forecast_periods, forecast_values, marker="o", linestyle="--", label="Forecast")
    ax.set_title("Projected Monthly Expenses")
    ax.set_xlabel("Month")
    ax.set_ylabel("Expense")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


st.title("💸 Personal Finance / Budget Dashboard")
st.caption("Upload a CSV of your transactions to explore spending patterns, savings progress, and future expense trends.")

with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    st.markdown("**Required columns:** date, category, description, amount")
    st.markdown("**Optional column:** type")
    savings_goal = st.number_input("Savings goal", min_value=0.0, value=5000.0, step=250.0)
    current_savings = st.number_input("Current savings toward goal", min_value=0.0, value=1200.0, step=100.0)
    forecast_periods = st.slider("Forecast months", min_value=1, max_value=6, value=3)

if uploaded_file is None:
    uploaded_file = "data/sample_budget_data.csv"
    st.info("No file uploaded yet, so the dashboard is using the included sample dataset.")

try:
    df = load_and_prepare_data(uploaded_file)
except DataValidationError as exc:
    st.error(str(exc))
    st.stop()

min_date = df["date"].min().date()
max_date = df["date"].max().date()

with st.sidebar:
    date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    available_categories = sorted(df["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Categories", options=available_categories, default=available_categories)

filtered_df = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df["date"].dt.date >= date_range[0]) & (filtered_df["date"].dt.date <= date_range[1])]
if selected_categories:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

if filtered_df.empty:
    st.warning("No transactions match the selected filters.")
    st.stop()

kpis = get_kpis(filtered_df)
monthly_df = monthly_summary(filtered_df)
category_df = category_expense_summary(filtered_df)
breakdown_df = monthly_category_breakdown(filtered_df)
forecast = expense_forecast(filtered_df, periods=forecast_periods)
goal = savings_goal_projection(filtered_df, goal_amount=savings_goal, current_savings=current_savings)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Income", currency(kpis["total_income"]))
col2.metric("Expenses", currency(kpis["total_expenses"]))
col3.metric("Net Cash Flow", currency(kpis["net_cash_flow"]))
col4.metric("Savings Rate", f"{kpis['savings_rate']:.1f}%")

insight_col1, insight_col2, insight_col3 = st.columns(3)
insight_col1.info(f"Top expense month: {top_expense_month(filtered_df)}")
insight_col2.info(f"Average monthly savings: {currency(goal.average_monthly_savings)}")
insight_col3.info(f"Estimated goal date: {goal.target_date_estimate}")

left, right = st.columns(2)
with left:
    st.pyplot(line_chart(monthly_df), use_container_width=True)
with right:
    st.pyplot(category_bar_chart(category_df), use_container_width=True)

full_width = st.container()
with full_width:
    st.pyplot(stacked_category_chart(breakdown_df), use_container_width=True)

forecast_left, forecast_right = st.columns([2, 1])
with forecast_left:
    st.pyplot(forecast_chart(monthly_df, forecast.periods, forecast.predicted_expense), use_container_width=True)
with forecast_right:
    st.subheader("Forecast Summary")
    forecast_df = pd.DataFrame(
        {"Month": forecast.periods, "Predicted Expense": forecast.predicted_expense}
    )
    st.dataframe(forecast_df, use_container_width=True)
    st.subheader("Savings Goal")
    st.write(f"Target amount: {currency(savings_goal)}")
    st.write(f"Current saved: {currency(current_savings)}")
    st.write(f"Monthly goal pace: {currency(goal.monthly_goal)}")
    st.write(f"On track: {'Yes' if goal.on_track else 'No'}")

st.subheader("Transactions")
st.dataframe(
    filtered_df[["date", "category", "description", "type", "amount"]].sort_values("date", ascending=False),
    use_container_width=True,
)
