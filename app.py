"""
FinTrack - Personal Expense & Budget Tracker
Main Flask Application Server
"""

import os
import csv
import io
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, Response
)

import database as db

app = Flask(__name__)
app.secret_key = "fintrack-secure-secret-key-student-portfolio-2026"

# Initialize SQLite database on startup
db.init_db()


@app.context_processor
def inject_global_vars():
    """Injects categories, payment methods, and current month into all templates."""
    today = datetime.now()
    return {
        "current_month": today.strftime("%Y-%m"),
        "today_date": today.strftime("%Y-%m-%d"),
        "expense_categories": db.EXPENSE_CATEGORIES,
        "income_categories": db.INCOME_CATEGORIES,
        "all_categories": db.EXPENSE_CATEGORIES + db.INCOME_CATEGORIES,
        "payment_methods": db.PAYMENT_METHODS,
        "now": today
    }


# -------------------------------------------------------------
# DASHBOARD / HOME ROUTE
# -------------------------------------------------------------
@app.route("/")
def index():
    """Dashboard view showcasing key financial KPIs, charts, and recent activity."""
    selected_month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    
    summary = db.get_dashboard_summary(selected_month)
    category_spending = db.get_category_breakdown(selected_month, tx_type="Expense")
    category_income = db.get_category_breakdown(selected_month, tx_type="Income")
    trends = db.get_monthly_trends(months_count=6)
    budget_data = db.get_budgets_with_actuals(selected_month)
    recent_transactions = db.get_transactions(limit=6)

    # Calculate top expense category
    top_expense = category_spending[0] if category_spending else None

    return render_template(
        "index.html",
        active_page="dashboard",
        selected_month=selected_month,
        summary=summary,
        category_spending=category_spending,
        category_income=category_income,
        trends=trends,
        budget_data=budget_data,
        recent_transactions=recent_transactions,
        top_expense=top_expense
    )


# -------------------------------------------------------------
# TRANSACTIONS MANAGEMENT
# -------------------------------------------------------------
@app.route("/transactions")
def transactions():
    """Transaction management page with filters, search, and pagination."""
    tx_type = request.args.get("type", "All")
    category = request.args.get("category", "All")
    month = request.args.get("month", "")
    search = request.args.get("search", "").strip()
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    
    page = int(request.args.get("page", 1))
    per_page = 12
    offset = (page - 1) * per_page

    tx_list = db.get_transactions(
        tx_type=tx_type,
        category=category,
        month=month if month else None,
        search=search if search else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        limit=per_page,
        offset=offset
    )

    total_count = db.get_transaction_count(
        tx_type=tx_type,
        category=category,
        month=month if month else None,
        search=search if search else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    return render_template(
        "transactions.html",
        active_page="transactions",
        transactions=tx_list,
        current_page=page,
        total_pages=total_pages,
        total_count=total_count,
        filter_type=tx_type,
        filter_category=category,
        filter_month=month,
        filter_search=search,
        filter_start_date=start_date,
        filter_end_date=end_date
    )


@app.route("/transactions/add", methods=["POST"])
def add_transaction_route():
    """Handles adding a new income or expense transaction."""
    title = request.form.get("title", "").strip()
    amount = request.form.get("amount", 0)
    tx_type = request.form.get("type", "Expense")
    category = request.form.get("category", "Other Expense")
    payment_method = request.form.get("payment_method", "UPI / GPay / PhonePe")
    date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
    notes = request.form.get("notes", "").strip()

    if not title or not amount:
        flash("Please provide both title and amount.", "error")
        return redirect(request.referrer or url_for("transactions"))

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be greater than 0.", "error")
            return redirect(request.referrer or url_for("transactions"))
            
        db.add_transaction(title, amount, tx_type, category, payment_method, date, notes)
        flash(f"Successfully recorded {tx_type.lower()}: '{title}' (₹{amount:,.2f})", "success")
    except ValueError:
        flash("Invalid amount format.", "error")
    except Exception as e:
        flash(f"Error saving transaction: {str(e)}", "error")

    return redirect(request.referrer or url_for("transactions"))


@app.route("/transactions/edit/<int:tx_id>", methods=["GET", "POST"])
def edit_transaction_route(tx_id):
    """Handles updating an existing transaction."""
    tx = db.get_transaction(tx_id)
    if not tx:
        flash("Transaction not found.", "error")
        return redirect(url_for("transactions"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", 0)
        tx_type = request.form.get("type", tx["type"])
        category = request.form.get("category", tx["category"])
        payment_method = request.form.get("payment_method", tx["payment_method"])
        date = request.form.get("date", tx["date"])
        notes = request.form.get("notes", "").strip()

        try:
            amount = float(amount)
            db.update_transaction(tx_id, title, amount, tx_type, category, payment_method, date, notes)
            flash("Transaction updated successfully.", "success")
            return redirect(url_for("transactions"))
        except Exception as e:
            flash(f"Error updating transaction: {str(e)}", "error")

    return render_template("edit_transaction.html", tx=tx, active_page="transactions")


@app.route("/transactions/delete/<int:tx_id>", methods=["POST"])
def delete_transaction_route(tx_id):
    """Deletes a transaction."""
    success = db.delete_transaction(tx_id)
    if success:
        flash("Transaction deleted successfully.", "info")
    else:
        flash("Failed to delete transaction.", "error")
    return redirect(request.referrer or url_for("transactions"))


# -------------------------------------------------------------
# BUDGET PLANNER
# -------------------------------------------------------------
@app.route("/budgets", methods=["GET", "POST"])
def budgets():
    """Budget management page."""
    selected_month = request.args.get("month", datetime.now().strftime("%Y-%m"))

    if request.method == "POST":
        category = request.form.get("category")
        month = request.form.get("month", selected_month)
        amount = request.form.get("amount", 0)

        try:
            amount = float(amount)
            if amount < 0:
                flash("Budget amount cannot be negative.", "error")
            else:
                db.set_budget(category, month, amount)
                flash(f"Budget of ₹{amount:,.2f} set for '{category}' for {month}.", "success")
        except ValueError:
            flash("Invalid budget amount.", "error")
        return redirect(url_for("budgets", month=month))

    budget_data = db.get_budgets_with_actuals(selected_month)
    return render_template(
        "budgets.html",
        active_page="budgets",
        selected_month=selected_month,
        budget_data=budget_data
    )


@app.route("/budgets/delete/<int:budget_id>", methods=["POST"])
def delete_budget_route(budget_id):
    """Deletes a budget limit."""
    month = request.form.get("month", datetime.now().strftime("%Y-%m"))
    db.delete_budget(budget_id)
    flash("Budget deleted successfully.", "info")
    return redirect(url_for("budgets", month=month))


# -------------------------------------------------------------
# ANALYTICS & INSIGHTS
# -------------------------------------------------------------
@app.route("/analytics")
def analytics():
    """Deep-dive analytics: category breakdowns, payment methods, monthly trends."""
    selected_month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    
    summary = db.get_dashboard_summary(selected_month)
    category_expenses = db.get_category_breakdown(selected_month, tx_type="Expense")
    category_incomes = db.get_category_breakdown(selected_month, tx_type="Income")
    payment_breakdown = db.get_payment_method_breakdown(selected_month)
    trends = db.get_monthly_trends(months_count=12)

    # Calculate average daily spend for the month
    try:
        dt = datetime.strptime(selected_month, "%Y-%m")
        # Days in month (approx or current day if this month)
        today = datetime.now()
        if dt.year == today.year and dt.month == today.month:
            days_passed = max(1, today.day)
        else:
            days_passed = 30
        avg_daily_spend = round(summary["total_expense"] / days_passed, 2)
    except Exception:
        avg_daily_spend = 0.0

    return render_template(
        "analytics.html",
        active_page="analytics",
        selected_month=selected_month,
        summary=summary,
        category_expenses=category_expenses,
        category_incomes=category_incomes,
        payment_breakdown=payment_breakdown,
        trends=trends,
        avg_daily_spend=avg_daily_spend
    )


# -------------------------------------------------------------
# CSV EXPORT ROUTE
# -------------------------------------------------------------
@app.route("/export/csv")
def export_csv():
    """Generates and downloads a CSV export of all transactions."""
    month = request.args.get("month", "")
    tx_list = db.get_transactions(month=month if month else None)

    si = io.StringIO()
    writer = csv.writer(si)
    # Header
    writer.writerow(["ID", "Date", "Title", "Type", "Category", "Amount (INR)", "Payment Method", "Notes", "Created At"])

    for tx in tx_list:
        writer.writerow([
            tx["id"],
            tx["date"],
            tx["title"],
            tx["type"],
            tx["category"],
            f"{tx['amount']:.2f}",
            tx["payment_method"],
            tx["notes"] or "",
            tx["created_at"]
        ])

    output = si.getvalue()
    filename = f"FinTrack_Transactions_{month if month else 'All'}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# -------------------------------------------------------------
# DEMO DATA & RESET UTILITIES
# -------------------------------------------------------------
@app.route("/seed-demo", methods=["POST"])
def seed_demo():
    """Loads realistic sample demo data for quick review and testing."""
    db.seed_demo_data()
    flash("🎉 Loaded sample demo data with realistic student/personal expenses and budgets!", "success")
    return redirect(url_for("index"))


@app.route("/reset-data", methods=["POST"])
def reset_data():
    """Clears all transactions and budgets."""
    db.reset_all_data()
    flash("Database reset: All transactions and budgets cleared.", "info")
    return redirect(url_for("index"))


# -------------------------------------------------------------
# API ROUTE FOR ASYNC CHARTS
# -------------------------------------------------------------
@app.route("/api/chart-data")
def api_chart_data():
    """Returns aggregated JSON data for frontend Chart.js components."""
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    
    cat_expenses = db.get_category_breakdown(month, tx_type="Expense")
    payment_methods = db.get_payment_method_breakdown(month)
    trends = db.get_monthly_trends(months_count=6)

    return jsonify({
        "categories": {
            "labels": [c["category"] for c in cat_expenses],
            "data": [c["total"] for c in cat_expenses]
        },
        "payment_methods": {
            "labels": [p["payment_method"] for p in payment_methods],
            "data": [p["total"] for p in payment_methods]
        },
        "trends": trends
    })


if __name__ == "__main__":
    # Run locally on port 5000 in debug mode
    print("\n" + "="*60)
    print("🚀 FinTrack Server Running at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
