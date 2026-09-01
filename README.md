# 💰 FinTrack - Personal Expense & Budget Tracker

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Frontend](https://img.shields.io/badge/UI-TailwindCSS_%26_Chart.js-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**FinTrack** is a modern, responsive personal finance and expense management web application crafted using **Python (Flask)**, **SQLite3**, **Tailwind CSS**, and **Chart.js**. Designed specifically for college students and young professionals to monitor their daily spending, budget limits, income sources, and cashflow trends with clean visual analytics.

---

## 🌟 Key Features

- 📊 **Interactive Financial Dashboard**:
  - Live metric KPI cards: *Total Income*, *Total Expense*, *Net Balance*, and *Savings Rate (%)*.
  - Category-wise Expense Breakdown via interactive **Chart.js** doughnut charts.
  - Multi-month Cashflow Trends (Income vs. Expense) via dual-bar charts.
  - Month-by-month filter to review past financial history instantly.

- 📝 **Comprehensive Transaction Management**:
  - Full CRUD support: Add, Edit, Delete Income & Expense entries.
  - Multi-criteria filtering: Search by keyword, transaction type (Income/Expense), category, and custom date ranges.
  - Pagination for optimal performance with large datasets.
  - Support for popular payment channels: *UPI / GPay / PhonePe*, *Debit Card*, *Credit Card*, *Cash*, *Net Banking*.

- 🎯 **Monthly Budget Goals & Threshold Warnings**:
  - Set spending thresholds for individual expense categories.
  - Real-time progress bars with dynamic status indicators:
    - 🟢 **On Track** (< 80% spent)
    - 🟡 **Near Limit** (80% - 99% spent)
    - 🔴 **Over Budget** (≥ 100% exceeded)

- 📈 **Deep Analytics & Insights**:
  - Average daily spend calculation for the active month.
  - Payment method distribution analytics.
  - 12-month historical cash flow trajectory line chart.
  - Category-wise summary table with percentage shares.

- 📥 **CSV Export & Backup**:
  - One-click export of complete transaction history to CSV format for Excel/Google Sheets analysis.

- 🪄 **1-Click Demo Data Generator**:
  - Pre-load realistic student/personal expenses & budgets to immediately test and showcase live charts.

- 🌓 **Modern Dark / Light Theme**:
  - Glassmorphic UI with seamless theme toggling persisted via `localStorage`.

---

## 🗄️ Database Architecture (SQLite)

FinTrack utilizes SQLite3 with parameterized queries to prevent SQL injection vulnerabilities and indexed columns for fast aggregation queries.

```
                    ┌─────────────────────────┐
                    │      transactions       │
                    ├─────────────────────────┤
                    │ id (PK, AUTOINCREMENT)  │
                    │ title (TEXT)            │
                    │ amount (REAL)           │
                    │ type (Income | Expense) │
                    │ category (TEXT)         │
                    │ payment_method (TEXT)   │
                    │ date (YYYY-MM-DD)       │
                    │ notes (TEXT)            │
                    │ created_at (TIMESTAMP)  │
                    └─────────────────────────┘
                                 ▲
                                 │
                    ┌─────────────────────────┐
                    │         budgets         │
                    ├─────────────────────────┤
                    │ id (PK, AUTOINCREMENT)  │
                    │ category (TEXT)         │
                    │ month (YYYY-MM)         │
                    │ amount (REAL)           │
                    │ UNIQUE(category, month) │
                    └─────────────────────────┘
```

---

## 📁 Project Directory Structure

```plaintext
Personal-Expense-Tracker/
│
├── app.py                  # Main Flask application & route controllers
├── database.py             # SQLite connection, schema, CRUD & aggregation logic
├── requirements.txt        # Python dependency manifest
├── run.bat                 # One-click Windows runner script
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with navbar, dark mode & global modal
│   ├── index.html          # Main financial dashboard & chart widgets
│   ├── transactions.html   # Searchable & filterable transactions ledger
│   ├── edit_transaction.html # Update transaction form
│   ├── budgets.html        # Category budget goal manager
│   └── analytics.html      # In-depth analytics & payment breakdowns
│
└── static/
    ├── css/
    │   └── custom.css      # Custom styling, scrollbars, and animations
    └── js/
        └── main.js         # Interactive UI controls and theme switcher
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+** installed on your system.

### Quick Start (Windows)
1. Double-click the **`run.bat`** file located in this folder.
2. It will automatically verify dependencies, start the local server, and launch the dashboard in your default browser at `http://127.0.0.1:5000`.

### Manual Setup via Terminal
1. Open PowerShell or Command Prompt inside this folder:
   ```bash
   cd C:\Users\adars\OneDrive\Desktop\Personal-Expense-Tracker
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Launch the application:
   ```bash
   python app.py
   ```

5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 📤 Pushing this Project to GitHub

To publish this project to your GitHub profile ([adarshkumar756390-dotcom](https://github.com/adarshkumar756390-dotcom)):

1. Go to [GitHub New Repository](https://github.com/new) and create a repository named **`Personal-Expense-Tracker`** (leave "Initialize with README" unchecked).
2. Open PowerShell in this project folder and run:
   ```powershell
   git remote add origin https://github.com/adarshkumar756390-dotcom/Personal-Expense-Tracker.git
   git branch -M main
   git push -u origin main
   ```

---

## 🎓 Author & Credits
- **Developer**: Adarsh Kumar ([GitHub Profile](https://github.com/adarshkumar756390-dotcom))
- **Role**: 2nd Year Computer Science / IT Student Project
- Built with Python, Flask, SQLite3, Tailwind CSS & Chart.js.
