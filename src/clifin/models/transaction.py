from dataclasses import dataclass
import sqlite3


@dataclass
class TransactionUpdate:
    """Represents fields to update in a transaction.

    All fields are optional - only non-None fields will be updated.
    This provides type safety and clarity over using **kwargs.
    """

    title: str | None = None
    amount: float | None = None
    category: str | None = None
    description: str | None = None
    date: str | None = None

    def has_updates(self) -> bool:
        """Check if any field has a value to update.

        Returns:
            bool: True if at least one field is not None
        """
        return any(
            [
                self.title is not None,
                self.amount is not None,
                self.category is not None,
                self.description is not None,
                self.date is not None,
            ]
        )

    def to_dict(self) -> dict[str, str | float]:
        """Convert to dictionary, excluding None values.

        Returns:
            dict: Non-None fields only
        """
        result: dict[str, str | float] = {}
        if self.title is not None:
            result["title"] = self.title
        if self.amount is not None:
            result["amount"] = self.amount
        if self.category is not None:
            result["category"] = self.category
        if self.description is not None:
            result["description"] = self.description
        if self.date is not None:
            result["date"] = self.date
        return result


@dataclass
class Transaction:
    """Represents a financial transaction (revenue or expense)."""

    id: int | None
    title: str
    amount: float
    category: str
    date: str
    description: str | None = None
    created_at: str | None = None

    def is_expense(self) -> bool:
        """Check if transaction is an expense (negative amount)."""
        return self.amount < 0

    def is_revenue(self) -> bool:
        """Check if transaction is a revenue (positive amount)."""
        return self.amount > 0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Transaction":
        """Create Transaction from database row.

        Args:
            row: sqlite3.Row object

        Returns:
            Transaction instance
        """
        return cls(
            id=row["id"],
            title=row["title"],
            amount=row["amount"],
            category=row["category"],
            date=row["date"],
            description=row["description"],
            created_at=row["created_at"],
        )
