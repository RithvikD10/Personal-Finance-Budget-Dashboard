from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import category_expense_summary, expense_forecast, monthly_category_breakdown, monthly_summary

ROOT = Path('/mnt/data/personal_finance_dashboard')
DATA_DIR = ROOT / 'data'
ASSETS_DIR = ROOT / 'assets'


def build_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    months = pd.period_range('2024-07', '2025-12', freq='M')
    rows = []

    for i, month in enumerate(months):
        start = month.to_timestamp()
        salary = 4200 + (i % 3) * 50
        freelance = 250 if i % 4 == 0 else 0

        rows.append([start + pd.Timedelta(days=0), 'Salary', 'Primary paycheck', salary, 'Income'])
        if freelance:
            rows.append([start + pd.Timedelta(days=4), 'Side Hustle', 'Freelance work', freelance, 'Income'])

        expenses = {
            'Rent': -(1450 + i * 8),
            'Groceries': -(360 + (i % 5) * 18 + rng.integers(-20, 25)),
            'Dining': -(120 + (i % 4) * 15 + rng.integers(-15, 20)),
            'Transportation': -(95 + rng.integers(-10, 16)),
            'Utilities': -(130 + rng.integers(-12, 15)),
            'Subscriptions': -48,
            'Shopping': -(85 + rng.integers(-25, 55)),
            'Entertainment': -(75 + rng.integers(-20, 35)),
            'Travel': -(220 + rng.integers(-70, 90)) if month.month in {8, 12} else 0,
        }

        day = 1
        for category, amount in expenses.items():
            if amount == 0:
                continue
            rows.append([
                start + pd.Timedelta(days=day),
                category,
                f'{category} expense',
                amount,
                'Expense',
            ])
            day += 3

    df = pd.DataFrame(rows, columns=['date', 'category', 'description', 'amount', 'type'])
    df = df.sort_values('date').reset_index(drop=True)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    return df


def save_sample_data(df: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_DIR / 'sample_budget_data.csv', index=False)



def save_overview_chart(monthly_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_df['month'], monthly_df['Income'], marker='o', label='Income')
    ax.plot(monthly_df['month'], monthly_df['Expense'], marker='o', label='Expenses')
    ax.plot(monthly_df['month'], monthly_df['Net'], marker='o', label='Net Cash Flow')
    ax.set_title('Budget Dashboard Overview')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / 'dashboard_overview.png', dpi=180)
    plt.close(fig)



def save_category_chart(category_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    top = category_df.head(8)
    ax.bar(top['category'], top['amount'])
    ax.set_title('Top Expense Categories')
    ax.set_xlabel('Category')
    ax.set_ylabel('Expense')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / 'category_breakdown.png', dpi=180)
    plt.close(fig)



def save_forecast_chart(monthly_df: pd.DataFrame, periods: list[str], values: list[float]) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_df['month'], monthly_df['Expense'], marker='o', label='Historical Expenses')
    ax.plot(periods, values, marker='o', linestyle='--', label='Forecast')
    ax.set_title('Expense Forecast')
    ax.set_xlabel('Month')
    ax.set_ylabel('Expense')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / 'expense_forecast.png', dpi=180)
    plt.close(fig)



def save_mix_chart(breakdown_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    categories = [col for col in breakdown_df.columns if col != 'month']
    bottom = np.zeros(len(breakdown_df))
    for category in categories:
        vals = breakdown_df[category].to_numpy()
        ax.bar(breakdown_df['month'], vals, bottom=bottom, label=category)
        bottom = bottom + vals
    ax.set_title('Monthly Expense Mix')
    ax.set_xlabel('Month')
    ax.set_ylabel('Expense')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(axis='y', alpha=0.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / 'expense_mix.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    df = build_sample_data()
    save_sample_data(df)
    monthly_df = monthly_summary(df)
    category_df = category_expense_summary(df)
    breakdown_df = monthly_category_breakdown(df)
    forecast = expense_forecast(df, periods=4)

    save_overview_chart(monthly_df)
    save_category_chart(category_df)
    save_forecast_chart(monthly_df, forecast.periods, forecast.predicted_expense)
    save_mix_chart(breakdown_df)
