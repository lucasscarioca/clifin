import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.clifin.repositories.transaction_repository import TransactionRepository

st.set_page_config(page_title="Clifin Dashboard", page_icon="💰", layout="wide")

repo = TransactionRepository()


def main():
    st.title("💰 Clifin Financial Dashboard")

    # Get data
    transactions = repo.get_all()
    total_balance = repo.get_total_balance()
    balance_by_category = repo.get_balance_by_category()

    if not transactions:
        st.info("No transactions yet. Add some transactions to see insights!")
        return

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(
        [
            {
                "id": t.id,
                "title": t.title,
                "amount": t.amount,
                "category": t.category,
                "date": t.date,
                "description": t.description,
                "created_at": t.created_at,
                "is_expense": t.is_expense(),
                "is_revenue": t.is_revenue(),
            }
            for t in transactions
        ]
    )

    df["date"] = pd.to_datetime(df["date"])
    df["amount_abs"] = df["amount"].abs()

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Balance", f"${total_balance:.2f}")

    with col2:
        total_revenue = df[df["is_revenue"]]["amount"].sum()
        st.metric("Total Revenue", f"${total_revenue:.2f}")

    with col3:
        total_expenses = df[df["is_expense"]]["amount_abs"].sum()
        st.metric("Total Expenses", f"${total_expenses:.2f}")

    with col4:
        transaction_count = len(df)
        st.metric("Total Transactions", transaction_count)

    st.divider()

    # Charts section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Balance by Category")
        if balance_by_category:
            fig, ax = plt.subplots(figsize=(8, 6))
            categories = list(balance_by_category.keys())
            balances = list(balance_by_category.values())
            colors = ["green" if b >= 0 else "red" for b in balances]
            ax.bar(categories, balances, color=colors)
            ax.set_ylabel("Balance ($)")
            ax.set_title("Balance by Category")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No category data available")

    with col2:
        st.subheader("Monthly Trends")
        df["month"] = df["date"].dt.to_period("M")
        monthly_data = df.groupby("month")["amount"].sum().reset_index()
        monthly_data["month"] = monthly_data["month"].astype(str)

        if not monthly_data.empty:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(monthly_data["month"], monthly_data["amount"], marker="o")
            ax.set_ylabel("Net Amount ($)")
            ax.set_title("Monthly Net Income/Expense")
            ax.axhline(y=0, color="black", linestyle="--", alpha=0.5)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("Not enough data for monthly trends")

    st.divider()

    # Recent Transactions
    st.subheader("Recent Transactions")
    recent_df = df.sort_values("date", ascending=False).head(10)

    if not recent_df.empty:
        # Format for display
        display_df = recent_df[["date", "title", "category", "amount"]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
        display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:.2f}")

        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No recent transactions")

    # Category breakdown
    st.subheader("Category Analysis")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Revenue by Category**")
        revenue_by_cat = df[df["is_revenue"]].groupby("category")["amount"].sum()
        if not revenue_by_cat.empty:
            st.dataframe(
                revenue_by_cat.sort_values(ascending=False), use_container_width=True
            )
        else:
            st.info("No revenue data")

    with col2:
        st.write("**Expenses by Category**")
        expenses_by_cat = df[df["is_expense"]].groupby("category")["amount_abs"].sum()
        if not expenses_by_cat.empty:
            st.dataframe(
                expenses_by_cat.sort_values(ascending=False), use_container_width=True
            )
        else:
            st.info("No expense data")


if __name__ == "__main__":
    main()
