from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"date", "category", "description", "amount"}


@dataclass
class ForecastResult:
    periods: List[str]
    predicted_expense: List[float]


@dataclass
class SavingsGoalResult:
    monthly_goal: float
    average_monthly_savings: float
    target_date_estimate: str
    on_track: bool


class DataValidationError(ValueError):
    """Raised when the uploaded finance file is missing required fields."""


def load_and_prepare_data(file) -> pd.DataFrame:
    """Load uploaded CSV or path and normalize columns."""
    df = pd.read_csv(file)
    df.columns = [str(col).strip().lower() for col in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise DataValidationError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            "Expected columns include date, category, description, and amount."
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["date", "amount", "category", "description"]).copy()
    df["category"] = df["category"].astype(str).str.strip().str.title()
    df["description"] = df["description"].astype(str).str.strip()

    if "type" not in df.columns:
        df["type"] = np.where(df["amount"] >= 0, "Income", "Expense")
    else:
        df["type"] = df["type"].astype(str).str.strip().str.title()
        inferred_type = np.where(df["amount"] >= 0, "Income", "Expense")
        df["type"] = np.where(df["type"].isin(["Income", "Expense"]), df["type"], inferred_type)

    df["month"] = df["date"].dt.to_period("M").astype(str)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def get_kpis(df: pd.DataFrame) -> Dict[str, float]:
    income = df.loc[df["amount"] > 0, "amount"].sum()
    expenses = df.loc[df["amount"] < 0, "amount"].sum()
    net = income + expenses
    savings_rate = (net / income * 100) if income else 0.0
    return {
        "total_income": float(income),
        "total_expenses": float(abs(expenses)),
        "net_cash_flow": float(net),
        "savings_rate": float(savings_rate),
    }


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["month", "type"], as_index=False)["amount"]
        .sum()
        .pivot(index="month", columns="type", values="amount")
        .fillna(0)
        .reset_index()
    )
    if "Income" not in monthly.columns:
        monthly["Income"] = 0.0
    if "Expense" not in monthly.columns:
        monthly["Expense"] = 0.0
    monthly["Expense"] = monthly["Expense"].abs()
    monthly["Net"] = monthly["Income"] - monthly["Expense"]
    return monthly.sort_values("month").reset_index(drop=True)


def category_expense_summary(df: pd.DataFrame) -> pd.DataFrame:
    expense_df = df[df["amount"] < 0].copy()
    summary = (
        expense_df.groupby("category", as_index=False)["amount"]
        .sum()
        .assign(amount=lambda x: x["amount"].abs())
        .sort_values("amount", ascending=False)
        .reset_index(drop=True)
    )
    return summary


def monthly_category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    expense_df = df[df["amount"] < 0].copy()
    pivot = (
        expense_df.assign(amount=lambda x: x["amount"].abs())
        .pivot_table(index="month", columns="category", values="amount", aggfunc="sum", fill_value=0)
        .sort_index()
    )
    return pivot.reset_index()


def expense_forecast(df: pd.DataFrame, periods: int = 3) -> ForecastResult:
    monthly = monthly_summary(df)
    expense_series = monthly["Expense"].to_numpy(dtype=float)
    if len(expense_series) == 0:
        return ForecastResult(periods=[], predicted_expense=[])

    x = np.arange(len(expense_series), dtype=float)
    if len(expense_series) == 1:
        slope = 0.0
        intercept = expense_series[0]
    else:
        slope, intercept = np.polyfit(x, expense_series, 1)

    future_x = np.arange(len(expense_series), len(expense_series) + periods, dtype=float)
    preds = np.maximum(intercept + slope * future_x, 0)

    last_period = pd.Period(monthly["month"].iloc[-1], freq="M")
    future_periods = [str(last_period + i) for i in range(1, periods + 1)]
    return ForecastResult(
        periods=future_periods,
        predicted_expense=[round(float(val), 2) for val in preds],
    )


def savings_goal_projection(df: pd.DataFrame, goal_amount: float, current_savings: float = 0.0) -> SavingsGoalResult:
    monthly = monthly_summary(df)
    if monthly.empty:
        return SavingsGoalResult(
            monthly_goal=0.0,
            average_monthly_savings=0.0,
            target_date_estimate="Not enough data",
            on_track=False,
        )

    avg_savings = float(monthly["Net"].mean())
    remaining = max(goal_amount - current_savings, 0)

    if avg_savings <= 0:
        estimate = "Current trend will not reach the goal"
        on_track = False
    else:
        months_needed = int(np.ceil(remaining / avg_savings)) if remaining > 0 else 0
        last_period = pd.Period(monthly["month"].iloc[-1], freq="M")
        estimate = str(last_period + max(months_needed, 0))
        on_track = True

    monthly_goal = goal_amount / max(len(monthly), 1)
    return SavingsGoalResult(
        monthly_goal=round(float(monthly_goal), 2),
        average_monthly_savings=round(avg_savings, 2),
        target_date_estimate=estimate,
        on_track=on_track,
    )


def top_expense_month(df: pd.DataFrame) -> str:
    monthly = monthly_summary(df)
    if monthly.empty:
        return "No expense data"
    row = monthly.sort_values("Expense", ascending=False).iloc[0]
    return f"{row['month']} (${row['Expense']:,.0f})"
