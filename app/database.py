"""
SQLite database wrapper for LocalBudgetAI expense management.
Provides lightweight persistence for expense data.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)


class ExpenseDatabase:
    """
    Lightweight SQLite wrapper for expense data persistence.
    """

    def __init__(self, db_path: str = "data/expenses.db"):
        """
        Initialize the expense database.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path

        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Only create directory if there's a directory part
            os.makedirs(db_dir, exist_ok=True)

        # Initialize database
        self._init_database()
        logger.info(f"Initialized expense database at {db_path}")

    def _init_database(self):
        """Create the expenses table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index for better performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_date 
                ON expenses(date)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_category 
                ON expenses(category)
            """
            )

            conn.commit()
            logger.info("Database tables and indexes created/verified")

    def insert_expense(
        self, date: str, amount: float, category: str, description: str = ""
    ) -> int:
        """
        Insert a new expense record.

        Args:
            date (str): Expense date in YYYY-MM-DD format
            amount (float): Expense amount (negative for expenses, positive for income)
            category (str): Expense category
            description (str): Optional description

        Returns:
            int: ID of the inserted record

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not date or not category:
            raise ValueError("Date and category are required fields")

        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (date, amount, category, description)
                VALUES (?, ?, ?, ?)
            """,
                (date, amount, category, description),
            )

            expense_id = cursor.lastrowid
            conn.commit()

            logger.info(
                f"Inserted expense {expense_id}: {category} ${amount} on {date}"
            )
            return expense_id

    def fetch_expenses(
        self,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Fetch expenses from the database.

        Args:
            limit (Optional[int]): Maximum number of records to return
            category (Optional[str]): Filter by category
            start_date (Optional[str]): Filter from this date (YYYY-MM-DD)
            end_date (Optional[str]): Filter to this date (YYYY-MM-DD)

        Returns:
            pd.DataFrame: DataFrame containing expense records
        """
        query = (
            "SELECT id, date, amount, category, description, created_at FROM expenses"
        )
        params = []
        conditions = []

        if category:
            conditions.append("category = ?")
            params.append(category)

        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY date DESC, id DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)

            if not df.empty:
                # Convert date column to datetime for better handling
                df["date"] = pd.to_datetime(df["date"])

            logger.info(f"Fetched {len(df)} expense records")
            return df

    def update_expense(
        self,
        expense_id: int,
        date: str,
        amount: float,
        category: str,
        description: str = "",
    ) -> bool:
        """
        Update an existing expense record.

        Args:
            expense_id (int): ID of the expense to update
            date (str): Updated date in YYYY-MM-DD format
            amount (float): Updated amount
            category (str): Updated category
            description (str): Updated description

        Returns:
            bool: True if update was successful, False if record not found

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not date or not category:
            raise ValueError("Date and category are required fields")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE expenses 
                SET date = ?, amount = ?, category = ?, description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (date, amount, category, description, expense_id),
            )

            updated = cursor.rowcount > 0
            conn.commit()

            if updated:
                logger.info(
                    f"Updated expense {expense_id}: {category} ${amount} on {date}"
                )
            else:
                logger.warning(f"No expense found with ID {expense_id}")

            return updated

    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense record.

        Args:
            expense_id (int): ID of the expense to delete

        Returns:
            bool: True if deletion was successful, False if record not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

            deleted = cursor.rowcount > 0
            conn.commit()

            if deleted:
                logger.info(f"Deleted expense {expense_id}")
            else:
                logger.warning(f"No expense found with ID {expense_id}")

            return deleted

    def get_expense_by_id(self, expense_id: int) -> Optional[Dict]:
        """
        Get a single expense record by ID.

        Args:
            expense_id (int): ID of the expense to retrieve

        Returns:
            Optional[Dict]: Expense record as dictionary, None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, date, amount, category, description, created_at
                FROM expenses WHERE id = ?
            """,
                (expense_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "date": row[1],
                    "amount": row[2],
                    "category": row[3],
                    "description": row[4],
                    "created_at": row[5],
                }
            return None

    def get_categories(self) -> List[str]:
        """
        Get all unique categories from the database.

        Returns:
            List[str]: List of unique categories
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
            categories = [row[0] for row in cursor.fetchall()]
            return categories

    def get_database_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dict: Statistics about the database
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total records
            cursor.execute("SELECT COUNT(*) FROM expenses")
            total_records = cursor.fetchone()[0]

            # Total expenses and income
            cursor.execute("SELECT SUM(amount) FROM expenses WHERE amount < 0")
            total_expenses = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(amount) FROM expenses WHERE amount > 0")
            total_income = cursor.fetchone()[0] or 0

            # Date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM expenses")
            date_range = cursor.fetchone()

            # Category count
            cursor.execute("SELECT COUNT(DISTINCT category) FROM expenses")
            category_count = cursor.fetchone()[0]

            return {
                "total_records": total_records,
                "total_expenses": abs(total_expenses),
                "total_income": total_income,
                "net_savings": total_income + total_expenses,  # expenses are negative
                "date_range": date_range,
                "category_count": category_count,
            }

    def import_from_dataframe(self, df: pd.DataFrame) -> int:
        """
        Import expenses from a pandas DataFrame.

        Args:
            df (pd.DataFrame): DataFrame with columns: date, amount, category, description

        Returns:
            int: Number of records imported

        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ["date", "amount", "category"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Ensure description column exists
        if "description" not in df.columns:
            df["description"] = ""

        imported_count = 0

        for _, row in df.iterrows():
            try:
                # Convert date to string format if it's a datetime
                date_str = row["date"]
                if pd.isna(date_str):
                    continue

                if isinstance(date_str, pd.Timestamp):
                    date_str = date_str.strftime("%Y-%m-%d")
                elif isinstance(date_str, str):
                    # Try to parse and reformat to ensure consistency
                    try:
                        parsed_date = pd.to_datetime(date_str)
                        date_str = parsed_date.strftime("%Y-%m-%d")
                    except:
                        continue

                # Skip if amount is invalid
                if pd.isna(row["amount"]) or not isinstance(
                    row["amount"], (int, float)
                ):
                    continue

                # Skip if category is invalid
                if pd.isna(row["category"]) or not row["category"]:
                    continue

                description = row.get("description", "") or ""
                if pd.isna(description):
                    description = ""

                self.insert_expense(
                    date=date_str,
                    amount=float(row["amount"]),
                    category=str(row["category"]),
                    description=str(description),
                )
                imported_count += 1

            except Exception as e:
                logger.warning(f"Failed to import row: {e}")
                continue

        logger.info(f"Imported {imported_count} expenses from DataFrame")
        return imported_count
