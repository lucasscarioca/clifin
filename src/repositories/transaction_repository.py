from src.db.database import get_connection
from src.models.transaction import Transaction, TransactionUpdate


class TransactionRepository:
    """Repository for managing financial transactions in the database."""

    def create(self, transaction: Transaction) -> int | None:
        """Insert a new transaction.

        Args:
            transaction: Transaction to insert

        Returns:
            int: ID of created transaction

        Raises:
            RuntimeError: If database operation fails
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                """
                INSERT INTO transactions (title, amount, category, description, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    transaction.title,
                    transaction.amount,
                    transaction.category,
                    transaction.description,
                    transaction.date,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Get transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction if found, None otherwise
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
            )
            row = cursor.fetchone()
            return Transaction.from_row(row) if row else None

    def get_all(self) -> list[Transaction]:
        """Get all transactions.

        Returns:
            List of all transactions
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                "SELECT * FROM transactions ORDER BY date DESC, created_at DESC"
            )
            rows = cursor.fetchall()
            return [Transaction.from_row(row) for row in rows]

    def update(self, transaction_id: int, updates: TransactionUpdate) -> bool:
        """Update transaction fields.

        Args:
            transaction_id: Transaction ID
            updates: TransactionUpdate object with fields to update

        Returns:
            bool: True if updated, False if not found

        Example:
            updates = TransactionUpdate(title="New Title", amount=100.0)
            repo.update(transaction_id, updates)
        """
        # Convert to dict and filter out None values
        fields_to_update = updates.to_dict()

        if not fields_to_update:
            return False

        # Build dynamic UPDATE query
        set_clause = ", ".join(f"{field} = ?" for field in fields_to_update.keys())
        values = list(fields_to_update.values()) + [transaction_id]

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE transactions SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, transaction_id: int) -> bool:
        """Delete transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            bool: True if deleted, False if not found
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_total_balance(self) -> float:
        """Calculate total balance (sum of all transactions).

        Returns:
            float: Total balance
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) as total FROM transactions"
            )
            row = cursor.fetchone()
            return float(row["total"])

    def get_balance_by_category(self) -> dict[str, float]:
        """Get balance grouped by category.

        Returns:
            dict: Category -> balance mapping
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                """
                SELECT category, SUM(amount) as total
                FROM transactions
                GROUP BY category
                ORDER BY total DESC
                """
            )
            rows = cursor.fetchall()
            return {row["category"]: float(row["total"]) for row in rows}

    def get_transactions_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[Transaction]:
        """Get transactions within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of transactions in date range
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            _ = cursor.execute(
                """
                SELECT * FROM transactions
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC, created_at DESC
                """,
                (start_date, end_date),
            )
            rows = cursor.fetchall()
            return [Transaction.from_row(row) for row in rows]
