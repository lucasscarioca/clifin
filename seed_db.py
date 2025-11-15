#!/usr/bin/env python3
"""
Database seeding of mock financial transaction data.
"""

import random
from datetime import datetime, timedelta

from faker import Faker

from src.clifin.models.transaction import Transaction
from src.clifin.repositories.transaction_repository import TransactionRepository


def generate_mock_transactions(num_transactions: int = 200) -> list[Transaction]:
    fake = Faker()
    Faker.seed(42)  # For reproducible results
    random.seed(42)

    # Define realistic categories and their typical amounts
    revenue_categories = {
        "Salary": (2500, 8000),
        "Freelance": (200, 2000),
        "Investment": (50, 1000),
        "Business": (100, 5000),
        "Gift": (20, 500),
        "Refund": (10, 300),
        "Bonus": (100, 2000),
    }

    expense_categories = {
        "Food": (10, 200),
        "Transportation": (5, 150),
        "Entertainment": (15, 300),
        "Shopping": (20, 800),
        "Bills": (50, 400),
        "Healthcare": (30, 500),
        "Education": (50, 1000),
        "Travel": (100, 2000),
        "Home": (100, 800),
        "Insurance": (50, 300),
        "Subscription": (5, 50),
        "Personal Care": (10, 150),
    }

    transactions = []
    start_date = datetime.now() - timedelta(days=365)  # Last year

    for i in range(num_transactions):
        # Random date within the last year
        random_days = random.randint(0, 365)
        transaction_date = start_date + timedelta(days=random_days)

        # Decide if it's revenue or expense (60% expenses, 40% revenue for realism)
        is_revenue = random.random() < 0.4

        if is_revenue:
            category = random.choice(list(revenue_categories.keys()))
            min_amount, max_amount = revenue_categories[category]
            amount = round(random.uniform(min_amount, max_amount), 2)
        else:
            category = random.choice(list(expense_categories.keys()))
            min_amount, max_amount = expense_categories[category]
            amount = -round(
                random.uniform(min_amount, max_amount), 2
            )  # Negative for expenses

        # Generate realistic title based on category
        title_templates = {
            "Salary": ["Monthly Salary", "Bi-weekly Pay", "Salary Deposit"],
            "Freelance": ["Freelance Project", "Consulting Fee", "Side Gig"],
            "Investment": ["Dividend Payment", "Stock Sale", "Crypto Gain"],
            "Business": ["Business Income", "Service Revenue", "Product Sale"],
            "Gift": ["Birthday Gift", "Holiday Gift", "Cash Gift"],
            "Refund": ["Tax Refund", "Purchase Refund", "Service Refund"],
            "Bonus": ["Performance Bonus", "Year-end Bonus", "Overtime Pay"],
            "Food": ["Grocery Shopping", "Restaurant", "Coffee", "Lunch"],
            "Transportation": ["Gas", "Uber", "Bus Ticket", "Car Maintenance"],
            "Entertainment": ["Movie Tickets", "Concert", "Streaming Service"],
            "Shopping": ["Clothes", "Electronics", "Home Goods", "Online Purchase"],
            "Bills": ["Electricity", "Water", "Internet", "Phone Bill"],
            "Healthcare": ["Doctor Visit", "Pharmacy", "Dental Care"],
            "Education": ["Course Fee", "Books", "Online Learning"],
            "Travel": ["Flight Ticket", "Hotel", "Vacation Expense"],
            "Home": ["Rent", "Mortgage", "Home Repair", "Furniture"],
            "Insurance": ["Health Insurance", "Car Insurance", "Home Insurance"],
            "Subscription": ["Netflix", "Spotify", "Gym Membership", "Magazine"],
            "Personal Care": ["Haircut", "Spa", "Cosmetics", "Fitness"],
        }

        title = random.choice(title_templates[category])

        # Sometimes add description
        description = None
        if random.random() < 0.3:  # 30% chance of having a description
            if is_revenue:
                description = fake.sentence(nb_words=6)
            else:
                description = fake.sentence(nb_words=4)

        transaction = Transaction(
            id=None,
            title=title,
            amount=amount,
            category=category,
            date=transaction_date.strftime("%Y-%m-%d"),
            description=description,
        )

        transactions.append(transaction)

    # Sort by date for realism
    transactions.sort(key=lambda x: x.date)

    return transactions


def seed_database():
    print("🌱 Seeding database with mock financial data...")

    # Initialize database if needed
    from src.clifin.db.database import get_connection, init_db

    init_db()

    repo = TransactionRepository()

    # Clear existing data
    print("🧹 Clearing existing transactions...")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()

    # Generate and insert mock data
    transactions = generate_mock_transactions(200)
    print(f"📊 Generated {len(transactions)} mock transactions")

    inserted_count = 0
    for transaction in transactions:
        try:
            _transaction_id = repo.create(transaction)
            inserted_count += 1
        except Exception as e:
            print(f"❌ Error inserting transaction: {e}")
            continue

    print(f"✅ Successfully seeded database with {inserted_count} transactions")


if __name__ == "__main__":
    seed_database()
