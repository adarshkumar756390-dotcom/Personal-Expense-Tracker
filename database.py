"""
FinTrack - Database Management Module
Handles SQLite connection, schema creation, CRUD operations, budget tracking,
and analytics aggregations.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db")

EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Rent & Housing",
    "Utilities & Bills",
    "Transportation",
    "Entertainment",
    "Education & Courses",
    "Shopping & Lifestyle",
    "Health & Fitness",
    "Personal Care",
    "Travel",
    "Other Expense"
]

INCOME_CATEGORIES = [
    "Salary / Stipend",
    "Freelance",
    "Pocket Money",
    "Investment / Returns",
    "Gifts & Grants",
    "Other Income"
]

PAYMENT_METHODS = [
    "UPI / GPay / PhonePe",
    "Debit Card",
    "Credit Card",
    "Cash",
    "Net Banking"
]


def get_db_connection():
    """Establishes connection to SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initializes tables and indexes if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Income', 'Expense')),
            category TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            month TEXT NOT NULL,
            amount REAL NOT NULL,
            UNIQUE(category, month)
        )
    """)

    # Create indexes for speed on date, category, and month queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_budget_month ON budgets(month)")

    conn.commit()
    conn.close()


def add_transaction(title, amount, tx_type, category, payment_method, date, notes=""):
    """Adds a new transaction record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (title, amount, type, category, payment_method, date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title.strip(), float(amount), tx_type, category, payment_method, date, notes.strip() if notes else ""))
    tx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tx_id


def get_transaction(tx_id):
    """Fetches a single transaction by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_transaction(tx_id, title, amount, tx_type, category, payment_method, date, notes=""):
    """Updates an existing transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET title = ?, amount = ?, type = ?, category = ?, payment_method = ?, date = ?, notes = ?
        WHERE id = ?
    """, (title.strip(), float(amount), tx_type, category, payment_method, date, notes.strip() if notes else "", tx_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def delete_transaction(tx_id):
    """Deletes a transaction by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def get_transactions(tx_type=None, category=None, month=None, search=None, start_date=None, end_date=None, limit=None, offset=None):
    """
    Retrieves transactions with dynamic multi-criteria filtering and sorting by date descending.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    if tx_type and tx_type != "All":
        query += " AND type = ?"
        params.append(tx_type)

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    if search:
        query += " AND (title LIKE ? OR notes LIKE ? OR category LIKE ? OR payment_method LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY date DESC, id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(int(limit))
        if offset is not None:
            query += " OFFSET ?"
            params.append(int(offset))

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_transaction_count(tx_type=None, category=None, month=None, search=None, start_date=None, end_date=None):
    """Gets total count for pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT COUNT(*) as count FROM transactions WHERE 1=1"
    params = []

    if tx_type and tx_type != "All":
        query += " AND type = ?"
        params.append(tx_type)

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)

    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    if search:
        query += " AND (title LIKE ? OR notes LIKE ? OR category LIKE ? OR payment_method LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    cursor.execute(query, params)
    count = cursor.fetchone()["count"]
    conn.close()
    return count


def get_dashboard_summary(month=None):
    """
    Computes total income, total expense, net balance, savings rate, and recent counts.
    If month is provided (e.g. '2026-09'), filters for that month.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    date_filter = "AND strftime('%Y-%m', date) = ?" if month else ""
    params = [month] if month else []

    # Income sum
    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'Income' {date_filter}", params)
    total_income = float(cursor.fetchone()["total"])

    # Expense sum
    cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = 'Expense' {date_filter}", params)
    total_expense = float(cursor.fetchone()["total"])

    # Total transactions count
    cursor.execute(f"SELECT COUNT(*) as count FROM transactions WHERE 1=1 {date_filter}", params)
    tx_count = int(cursor.fetchone()["count"])

    net_balance = total_income - total_expense
    savings_rate = round(((total_income - total_expense) / total_income * 100), 1) if total_income > 0 else 0.0

    conn.close()
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "savings_rate": savings_rate,
        "tx_count": tx_count
    }


def get_category_breakdown(month=None, tx_type="Expense"):
    """
    Returns spending aggregated by category with amount and percentage.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
        FROM transactions
        WHERE type = ?
    """
    params = [tx_type]

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    query += " GROUP BY category ORDER BY total DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    total_sum = sum(r["total"] for r in rows)
    results = []
    for r in rows:
        pct = round((r["total"] / total_sum * 100), 1) if total_sum > 0 else 0.0
        results.append({
            "category": r["category"],
            "total": float(r["total"]),
            "count": int(r["count"]),
            "percentage": pct
        })
    return results


def get_payment_method_breakdown(month=None):
    """Returns expense spending grouped by payment method."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT payment_method, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
        FROM transactions
        WHERE type = 'Expense'
    """
    params = []
    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    query += " GROUP BY payment_method ORDER BY total DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    total_sum = sum(r["total"] for r in rows)
    results = []
    for r in rows:
        pct = round((r["total"] / total_sum * 100), 1) if total_sum > 0 else 0.0
        results.append({
            "payment_method": r["payment_method"],
            "total": float(r["total"]),
            "count": int(r["count"]),
            "percentage": pct
        })
    return results


def get_monthly_trends(months_count=6):
    """
    Returns monthly income and expense totals for the past N months for charting.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query last N months aggregated
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', date) as month_str,
            COALESCE(SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END), 0) as income,
            COALESCE(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 0) as expense
        FROM transactions
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month_str DESC
        LIMIT ?
    """, (months_count,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        today = datetime.now()
        return {
            "labels": [today.strftime("%b %Y")],
            "income": [0.0],
            "expense": [0.0]
        }

    # Reverse to have chronological order (oldest to newest)
    rows = list(reversed(rows))
    
    labels = []
    income_data = []
    expense_data = []

    for r in rows:
        month_str = r["month_str"]
        try:
            dt = datetime.strptime(month_str, "%Y-%m")
            label = dt.strftime("%b %Y")
        except Exception:
            label = month_str
        labels.append(label)
        income_data.append(float(r["income"]))
        expense_data.append(float(r["expense"]))

    return {
        "labels": labels,
        "income": income_data,
        "expense": expense_data
    }


def set_budget(category, month, amount):
    """Sets or updates a monthly budget for a category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (category, month, amount)
        VALUES (?, ?, ?)
        ON CONFLICT(category, month) DO UPDATE SET amount = excluded.amount
    """, (category, month, float(amount)))
    conn.commit()
    conn.close()


def delete_budget(budget_id):
    """Deletes a budget entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
    conn.commit()
    conn.close()


def get_budgets_with_actuals(month):
    """
    Fetches all budgets for a given month alongside the actual amount spent in that category.
    Computes spent percentage, remaining balance, and alert status (safe, warning, danger).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get budgets
    cursor.execute("SELECT id, category, month, amount FROM budgets WHERE month = ? ORDER BY category ASC", (month,))
    budgets = cursor.fetchall()

    results = []
    total_budgeted = 0.0
    total_spent_budgeted = 0.0

    for b in budgets:
        cat = b["category"]
        limit_amt = float(b["amount"])
        total_budgeted += limit_amt

        # Calculate actual spent for this category and month
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as spent
            FROM transactions
            WHERE category = ? AND type = 'Expense' AND strftime('%Y-%m', date) = ?
        """, (cat, month))
        spent = float(cursor.fetchone()["spent"])
        total_spent_budgeted += spent

        remaining = limit_amt - spent
        pct = round((spent / limit_amt * 100), 1) if limit_amt > 0 else 0.0

        if pct >= 100:
            status = "danger" # Exceeded
        elif pct >= 80:
            status = "warning" # Near limit
        else:
            status = "safe" # Within limit

        results.append({
            "id": b["id"],
            "category": cat,
            "month": month,
            "budget": limit_amt,
            "spent": spent,
            "remaining": remaining,
            "percentage": pct,
            "status": status
        })

    conn.close()
    return {
        "budgets": results,
        "total_budgeted": total_budgeted,
        "total_spent": total_spent_budgeted,
        "overall_percentage": round((total_spent_budgeted / total_budgeted * 100), 1) if total_budgeted > 0 else 0.0
    }


def seed_demo_data():
    """
    Generates realistic, relatable transactions for testing and portfolio showcase.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")

    today = datetime.now()
    curr_month_str = today.strftime("%Y-%m")
    
    # Calculate previous 2 months
    m1 = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    m2 = ((today.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    months = [m2, m1, curr_month_str]

    # Sample template transactions
    sample_incomes = [
        ("Web Development Internship Stipend", 18000, "Salary / Stipend", "Net Banking"),
        ("Freelance Landing Page Project", 9500, "Freelance", "UPI / GPay / PhonePe"),
        ("Monthly Allowance / Pocket Money", 6000, "Pocket Money", "UPI / GPay / PhonePe"),
        ("Stock Dividend Return", 1200, "Investment / Returns", "Net Banking"),
    ]

    sample_expenses = [
        ("PG / Hostel Room Rent", 7500, "Rent & Housing", "Net Banking"),
        ("Campus Mess & Grocery Essentials", 3200, "Groceries", "UPI / GPay / PhonePe"),
        ("Weekend Cafe & Food Outing", 650, "Food & Dining", "UPI / GPay / PhonePe"),
        ("Zomato Pizza Order with Friends", 480, "Food & Dining", "UPI / GPay / PhonePe"),
        ("Electricity & WiFi Bill", 1100, "Utilities & Bills", "UPI / GPay / PhonePe"),
        ("Monthly Metro Card Recharge", 1200, "Transportation", "Debit Card"),
        ("Uber / Auto Ride", 240, "Transportation", "UPI / GPay / PhonePe"),
        ("Python & Web Dev Masterclass", 899, "Education & Courses", "Credit Card"),
        ("Netflix & Spotify Subscription", 499, "Entertainment", "Credit Card"),
        ("Gym Membership Fee", 1500, "Health & Fitness", "UPI / GPay / PhonePe"),
        ("Campus Stationary & Notebooks", 350, "Education & Courses", "Cash"),
        ("Casual T-shirt & Sneakers", 1850, "Shopping & Lifestyle", "Credit Card"),
    ]

    for m in months:
        y, mo = map(int, m.split("-"))
        # Add incomes for the month
        for title, amt, cat, pm in sample_incomes:
            day = random.randint(1, 5)
            date_str = f"{y:04d}-{mo:02d}-{day:02d}"
            cursor.execute("""
                INSERT INTO transactions (title, amount, type, category, payment_method, date, notes)
                VALUES (?, ?, 'Income', ?, ?, ?, ?)
            """, (title, amt + random.randint(-500, 500), cat, pm, date_str, "Monthly credited stipend/income"))

        # Add expenses for the month
        for title, amt, cat, pm in sample_expenses:
            day = random.randint(2, 28)
            if m == curr_month_str and day > today.day:
                day = max(1, today.day - random.randint(0, 3))
            date_str = f"{y:04d}-{mo:02d}-{day:02d}"
            amt_var = amt + random.randint(-50, 150)
            cursor.execute("""
                INSERT INTO transactions (title, amount, type, category, payment_method, date, notes)
                VALUES (?, ?, 'Expense', ?, ?, ?, ?)
            """, (title, amt_var, cat, pm, date_str, "Regular personal expense"))

    # Set sample budgets for current month
    default_budgets = [
        ("Food & Dining", 4000),
        ("Groceries", 4500),
        ("Rent & Housing", 8000),
        ("Transportation", 2000),
        ("Entertainment", 1500),
        ("Shopping & Lifestyle", 3000),
        ("Utilities & Bills", 1500),
        ("Education & Courses", 2000),
    ]

    for cat, amt in default_budgets:
        cursor.execute("""
            INSERT OR REPLACE INTO budgets (category, month, amount)
            VALUES (?, ?, ?)
        """, (cat, curr_month_str, amt))

    conn.commit()
    conn.close()
    return True


def reset_all_data():
    """Clears all records from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM budgets")
    conn.commit()
    conn.close()
