from typing_extensions import Annotated
from datetime import datetime
import subprocess
import typer

from src.db.database import init_db
from src.repositories.transaction_repository import TransactionRepository
from src.models.transaction import Transaction, TransactionUpdate

app = typer.Typer()
repo = TransactionRepository()


def validate_title(title: str):
    if not title:
        typer.echo("Title cannot be empty")
        raise typer.Abort()


def validate_date(date: str):
    if date:
        # If date is passed, we should validate if it valid YYYY-MM-DD
        if len(date) != 10 or date[4] != "-" or date[7] != "-":
            # TODO: properly validate this
            typer.echo("Date must be in YYYY-MM-DD format")
            raise typer.Abort()


def validate_amount(amount: str):
    if not amount.isdigit() or int(amount) <= 0:
        typer.echo("Amount must be a positive number")
        raise typer.Abort()


def validate_category(category: str):
    if not category:
        typer.echo("Category cannot be empty")
        raise typer.Abort()


@app.command()
def add(title: str, amount: str, category: str, description: str = "", date: str = ""):
    """(Add) Insert a new revenue."""
    validate_title(title)
    validate_amount(amount)
    validate_date(date)
    validate_category(category)

    # Use current date if not provided
    transaction_date = date if date else datetime.now().strftime("%Y-%m-%d")

    transaction = Transaction(
        id=None,
        title=title,
        amount=float(amount),
        category=category,
        description=description if description else None,
        date=transaction_date,
    )

    transaction_id = repo.create(transaction)
    typer.echo(
        f"✓ Added revenue #{transaction_id}: {title} (+${amount}) [{transaction_date}]"
    )


@app.command()
def sub(title: str, amount: str, category: str, description: str = "", date: str = ""):
    """(Subtract) Insert a new expense."""
    validate_title(title)
    validate_amount(amount)
    validate_date(date)
    validate_category(category)

    # Use current date if not provided
    transaction_date = date if date else datetime.now().strftime("%Y-%m-%d")

    # Store expenses as negative amounts
    transaction = Transaction(
        id=None,
        title=title,
        amount=-float(amount),  # Negative for expenses
        category=category,
        description=description if description else None,
        date=transaction_date,
    )

    transaction_id = repo.create(transaction)
    typer.echo(
        f"✓ Added expense #{transaction_id}: {title} (-${amount}) [{transaction_date}]"
    )


@app.command()
def delete(
    id: str,
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete this entry?")
    ],
):
    """Delete an entry from the database."""
    if not force:
        typer.echo("Operation cancelled.")
        raise typer.Abort()

    try:
        transaction_id = int(id)
    except ValueError:
        typer.echo("Error: ID must be a number")
        raise typer.Abort()

    # Check if exists first
    transaction = repo.get_by_id(transaction_id)
    if not transaction:
        typer.echo(f"Error: Transaction #{transaction_id} not found")
        raise typer.Abort()

    success = repo.delete(transaction_id)
    if success:
        typer.echo(f"✓ Deleted transaction #{transaction_id}: {transaction.title}")
    else:
        typer.echo(f"Error: Failed to delete transaction #{transaction_id}")


@app.command()
def update(
    id: str,
    title: str = "",
    amount: str = "",
    category: str = "",
    description: str = "",
    date: str = "",
):
    """Update an entry in the database."""
    validate_title(title) if title else None
    validate_amount(amount) if amount else None
    validate_date(date) if date else None
    validate_category(category) if category else None

    try:
        transaction_id = int(id)
    except ValueError:
        typer.echo("Error: ID must be a number")
        raise typer.Abort()

    # Check if exists
    if not repo.get_by_id(transaction_id):
        typer.echo(f"Error: Transaction #{transaction_id} not found")
        raise typer.Abort()

    # Build update object with only provided fields
    # This is type-safe and clearer than using **kwargs
    updates = TransactionUpdate(
        title=title if title else None,
        amount=float(amount) if amount else None,
        category=category if category else None,
        description=description if description else None,
        date=date if date else None,
    )

    # Check if user provided any updates
    if not updates.has_updates():
        typer.echo("No fields to update")
        raise typer.Abort()

    success = repo.update(transaction_id, updates)
    if success:
        typer.echo(f"✓ Updated transaction #{transaction_id}")
    else:
        typer.echo(f"Error: Failed to update transaction #{transaction_id}")


@app.command()
def init():
    """Initialize the database and run migrations."""
    try:
        init_db()

        # Run alembic migrations
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"], capture_output=True, text=True
        )

        if result.returncode == 0:
            typer.echo("✓ Database initialized and migrations applied successfully")
        else:
            typer.echo(f"Error running migrations: {result.stderr}")
            raise typer.Abort()
    except Exception as e:
        typer.echo(f"Error initializing database: {e}")
        raise typer.Abort()


@app.command()
def summary():
    """Show financial summary."""
    total_balance = repo.get_total_balance()
    balance_by_category = repo.get_balance_by_category()

    typer.echo("\n=== Financial Summary ===")
    typer.echo(f"Total Balance: ${total_balance:.2f}\n")

    if balance_by_category:
        typer.echo("Balance by Category:")
        for category, amount in balance_by_category.items():
            sign = "+" if amount >= 0 else ""
            typer.echo(f"  {category}: {sign}${amount:.2f}")
    else:
        typer.echo("No transactions yet")


@app.command()
def list():
    """List transactions."""
    transactions = repo.get_all()

    if not transactions:
        typer.echo("No transactions yet")
        return

    typer.echo("\n=== Transactions ===")
    typer.echo(f"{'ID':<5} {'Date':<12} {'Title':<20} {'Category':<15} {'Amount':<10}")
    typer.echo("-" * 70)

    for t in transactions[:20]:  # Show last 20
        amount_str = f"{'+' if t.amount >= 0 else ''}${t.amount:.2f}"
        typer.echo(
            f"{t.id:<5} {t.date:<12} {t.title[:20]:<20} {t.category[:15]:<15} {amount_str:<10}"
        )


if __name__ == "__main__":
    app()
