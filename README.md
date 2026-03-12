# Personal Finance / Budget Dashboard

A Python dashboard that turns a transaction CSV into clean budget visuals, trend analysis, expense forecasts, and savings goal tracking.

## Why this project stands out

This project is practical, polished, and easy to demo on GitHub. It combines business analytics and data storytelling by helping users:

- upload spending data from a CSV
- track income, expenses, and net cash flow
- break down spending by category and month
- forecast future expenses with a simple trend model
- estimate savings goal progress with a projected target month

## Features

- **CSV upload workflow** with a built in sample dataset
- **KPI cards** for income, expenses, net cash flow, and savings rate
- **Category analysis** to identify top spending areas
- **Monthly trend charts** for income, expenses, and net movement
- **Expense mix chart** to show how spending changes over time
- **Forecasting panel** for projected monthly expenses
- **Savings goal tracker** with estimated timeline
- **Transaction table** with filters for category and date range

## Tech stack

- Python
- Streamlit
- pandas
- NumPy
- Matplotlib
- pytest

## Project structure

```text
personal_finance_dashboard/
├── app.py
├── utils.py
├── requirements.txt
├── LICENSE
├── README.md
├── create_assets.py
├── data/
│   └── sample_budget_data.csv
├── assets/
│   ├── dashboard_overview.png
│   ├── category_breakdown.png
│   ├── expense_forecast.png
│   └── expense_mix.png
└── tests/
    └── test_utils.py
```

## Expected CSV format

Your uploaded file should include these columns:

| column | required | example |
|---|---|---|
| `date` | yes | `2025-01-15` |
| `category` | yes | `Groceries` |
| `description` | yes | `Trader Joe's` |
| `amount` | yes | `-85.40` |
| `type` | no | `Expense` or `Income` |

Positive amounts are treated as income. Negative amounts are treated as expenses.

## How to run locally

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd personal_finance_dashboard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the app

```bash
streamlit run app.py
```

The app opens with the included sample dataset, and you can replace it by uploading your own CSV.

## Sample insights from the included dataset

- rent is the largest recurring expense
- travel and shopping create noticeable spikes in a few months
- savings progress depends heavily on keeping discretionary spending under control
- the forecast gives a quick estimate of near term expense pressure

## Testing

Run the tests with:

```bash
pytest
```

## Ideas for future improvements

- recurring transaction detection
- more advanced forecasting models
- merchant level insights
- debt payoff planner
- exportable PDF summary report
- authentication and cloud deployment

## License

This project is licensed under the MIT License.
