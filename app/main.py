import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import ExpenseDatabase
from analyzer import (
    analyze_expenses_by_category,
    analyze_monthly_trend,
    generate_expense_summary_report,
)
from plotly_analyzer import (
    create_interactive_bar_chart,
    create_interactive_pie_chart,
    create_interactive_line_chart,
    create_dashboard_overview,
    create_category_comparison,
)
from llm_helper import (
    query_expense_ai,
    get_expense_context,
    check_ollama_status,
    get_available_models,
)
from advanced_llm_helper import (
    advanced_query_expense_ai,
    smart_expense_categorization,
    AdvancedFinancialAI,
)

# Configure page
st.set_page_config(
    page_title="LocalBudgetAI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def init_session_state():
    """Initialize session state variables for persistent UI state"""
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "date_range": None,
            "categories": [],
            "amount_range": None,
        }
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "📊 Dashboard"
    if "editing_expense" not in st.session_state:
        st.session_state.editing_expense = None
    if "preferred_ai_model" not in st.session_state:
        st.session_state.preferred_ai_model = "mistral"
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []


init_session_state()

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        text-align: center;
        margin-bottom: 1rem;
    }
    .upload-section {
        border: 2px dashed #cbd5e1;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        background-color: #f8fafc;
    }
    .form-section {
        border: 2px solid #e5e7eb;
        border-radius: 1rem;
        padding: 2rem;
        margin: 2rem 0;
        background-color: #f9fafb;
    }
    .error-box {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize database
@st.cache_resource
def get_database():
    """Initialize and return the database connection."""
    return ExpenseDatabase()


def create_sidebar_filters(db):
    """Create enhanced sidebar with filters and navigation"""
    st.sidebar.title("🧭 Navigation")

    # Navigation
    page = st.sidebar.radio(
        "Choose a section:",
        [
            "📊 Dashboard",
            "📁 Data Input",
            "📋 Manage Expenses",
            "📈 Analytics",
            "🤖 AI Assistant",
        ],
        key="navigation",
        index=[
            "📊 Dashboard",
            "📁 Data Input",
            "📋 Manage Expenses",
            "📈 Analytics",
            "🤖 AI Assistant",
        ].index(st.session_state.selected_page),
    )

    # Update session state
    st.session_state.selected_page = page

    # Filters section
    st.sidebar.markdown("---")
    st.sidebar.title("🔍 Filters")

    # Get available data for filter options
    stats = db.get_database_stats()

    if stats["total_records"] > 0:
        # Date range filter
        st.sidebar.subheader("📅 Date Range")

        # Get min and max dates from database
        expenses_df = db.fetch_expenses()
        if not expenses_df.empty:
            min_date = expenses_df["date"].min().date()
            max_date = expenses_df["date"].max().date()

            # Date range selector
            use_date_filter = st.sidebar.checkbox(
                "Filter by date range", key="use_date_filter"
            )

            if use_date_filter:
                date_range = st.sidebar.date_input(
                    "Select date range:",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="date_range_filter",
                )

                # Handle both single date and date range
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    st.session_state.filters["date_range"] = date_range
                else:
                    st.session_state.filters["date_range"] = (
                        (date_range, date_range) if date_range else None
                    )
            else:
                st.session_state.filters["date_range"] = None

        # Category filter
        st.sidebar.subheader("📊 Categories")
        categories = db.get_categories()

        if categories:
            selected_categories = st.sidebar.multiselect(
                "Select categories:",
                options=categories,
                default=st.session_state.filters.get("categories", []),
                key="category_filter",
            )
            st.session_state.filters["categories"] = selected_categories

        # Amount range filter
        st.sidebar.subheader("💰 Amount Range")
        use_amount_filter = st.sidebar.checkbox(
            "Filter by amount", key="use_amount_filter"
        )

        if use_amount_filter:
            # Get min and max amounts (absolute values for better UX)
            min_amount = float(expenses_df["amount"].abs().min())
            max_amount = float(expenses_df["amount"].abs().max())

            amount_range = st.sidebar.slider(
                "Amount range ($):",
                min_value=min_amount,
                max_value=max_amount,
                value=(min_amount, max_amount),
                step=1.0,
                key="amount_range_filter",
            )
            st.session_state.filters["amount_range"] = amount_range
        else:
            st.session_state.filters["amount_range"] = None

        # Quick filter buttons
        st.sidebar.subheader("⚡ Quick Filters")
        col1, col2 = st.sidebar.columns(2)

        with col1:
            if st.button("This Month", key="filter_this_month"):
                today = date.today()
                first_day = today.replace(day=1)
                st.session_state.filters["date_range"] = (first_day, today)
                st.rerun()

        with col2:
            if st.button("Last 30 Days", key="filter_last_30"):
                today = date.today()
                thirty_days_ago = today - timedelta(days=30)
                st.session_state.filters["date_range"] = (thirty_days_ago, today)
                st.rerun()

        # Clear filters button
        if st.sidebar.button("🔄 Clear All Filters", key="clear_filters"):
            st.session_state.filters = {
                "date_range": None,
                "categories": [],
                "amount_range": None,
            }
            st.rerun()

    else:
        st.sidebar.info("Add some data to enable filters!")

    # Filter summary
    if any(st.session_state.filters.values()):
        st.sidebar.markdown("---")
        st.sidebar.subheader("📋 Active Filters")

        if st.session_state.filters["date_range"]:
            start, end = st.session_state.filters["date_range"]
            st.sidebar.text(f"📅 {start} to {end}")

        if st.session_state.filters["categories"]:
            st.sidebar.text(
                f"📊 {len(st.session_state.filters['categories'])} categories"
            )

        if st.session_state.filters["amount_range"]:
            min_amt, max_amt = st.session_state.filters["amount_range"]
            st.sidebar.text(f"💰 ${min_amt:.0f} - ${max_amt:.0f}")

    return page


def apply_filters_to_dataframe(df, filters):
    """Apply filters to DataFrame based on session state"""
    if df.empty:
        return df

    filtered_df = df.copy()

    # Apply date range filter
    if filters.get("date_range"):
        start_date, end_date = filters["date_range"]
        filtered_df = filtered_df[
            (filtered_df["date"] >= pd.to_datetime(start_date))
            & (filtered_df["date"] <= pd.to_datetime(end_date))
        ]

    # Apply category filter
    if filters.get("categories"):
        filtered_df = filtered_df[filtered_df["category"].isin(filters["categories"])]

    # Apply amount range filter
    if filters.get("amount_range"):
        min_amount, max_amount = filters["amount_range"]
        # Filter by absolute amount to handle both income and expenses
        filtered_df = filtered_df[
            (filtered_df["amount"].abs() >= min_amount)
            & (filtered_df["amount"].abs() <= max_amount)
        ]

    return filtered_df


def validate_required_columns(df):
    """Validate that the uploaded CSV contains required columns with flexible matching"""
    # Define flexible mappings for different column name variations
    column_mappings = {
        "date": [
            "date",
            "Date",
            "DATE",
            "transaction_date",
            "transaction date",
            "trans_date",
            "time",
            "Time",
        ],
        "amount": [
            "amount",
            "Amount",
            "AMOUNT",
            "value",
            "Value",
            "price",
            "Price",
            "sum",
            "Sum",
            "total",
            "Total",
        ],
        "category": [
            "category",
            "Category",
            "CATEGORY",
            "type",
            "Type",
            "expense_type",
            "expense type",
            "class",
            "Class",
        ],
    }

    found_columns = {}
    missing_columns = []

    # Check each required column
    for required_col, variations in column_mappings.items():
        found = False
        for variation in variations:
            if variation in df.columns:
                found_columns[required_col] = variation
                found = True
                break

        if not found:
            missing_columns.append(required_col)

    return missing_columns, found_columns


def show_csv_upload_section(db):
    """Show CSV upload section"""
    st.subheader("📁 Upload CSV File")

    # Show format guidance
    with st.expander("📋 **CSV Format Guide** - Click to see expected format"):
        st.markdown(
            """
        ### ✅ Accepted Column Names (case-insensitive):
        
        **📅 Date Column:** `date`, `Date`, `transaction_date`, `time`  
        **💰 Amount Column:** `amount`, `Amount`, `value`, `price`, `total`  
        **🏷️ Category Column:** `category`, `Category`, `type`, `expense_type`  
        **📝 Description Column:** `description`, `desc`, `details`, `memo`, `note` *(optional)*
        
        ### 📄 Sample CSV Format:
        ```csv
        date,amount,category,description
        2024-01-15,-45.67,Groceries,Whole Foods Market
        2024-01-16,-12.50,Transportation,Metro Card
        2024-01-20,2500.00,Income,Salary Deposit
        ```
        
        ### 💡 Tips:
        - **Expenses**: Use negative amounts (e.g., `-45.67`)
        - **Income**: Use positive amounts (e.g., `2500.00`)
        - **Dates**: Any common format works (YYYY-MM-DD, MM/DD/YYYY, etc.)
        - **Categories**: Any text (Groceries, Food, Entertainment, etc.)
        """
        )

    uploaded_file = st.file_uploader(
        "Choose a CSV file containing your transaction data",
        type=["csv"],
        help="Upload your transaction data in CSV format. The system will automatically detect and map your column names.",
    )

    if uploaded_file is not None:
        try:
            # Load the CSV file
            df = pd.read_csv(uploaded_file)

            st.success(f"✅ File uploaded successfully! Loaded {len(df)} records.")

            # Show column detection info
            st.info(f"📋 **Detected columns:** {', '.join(df.columns.tolist())}")

            # Validate required columns with flexible matching
            missing_columns, found_columns = validate_required_columns(df)

            if missing_columns:
                st.markdown(
                    f"""
                <div class="error-box">
                    <h4>⚠️ Missing Required Columns</h4>
                    <p>The following required columns could not be found in your CSV:</p>
                    <ul>
                        {''.join([f'<li><strong>{col}</strong></li>' for col in missing_columns])}
                    </ul>
                    <p><strong>Found columns:</strong> {', '.join(found_columns.values()) if found_columns else 'None'}</p>
                    <p>Please ensure your CSV contains columns for: <strong>date</strong>, <strong>amount</strong>, and <strong>category</strong></p>
                    <p><em>Tip: Column names are case-insensitive and can have variations like 'Date', 'date', 'Amount', 'value', etc.</em></p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                return

            # Map columns to standard names
            df_mapped = df.copy()

            # Rename columns to standard names
            for standard_name, actual_name in found_columns.items():
                if actual_name != standard_name.title():
                    df_mapped = df_mapped.rename(
                        columns={actual_name: standard_name.title()}
                    )

            # Add Description column if missing
            if (
                "Description" not in df_mapped.columns
                and "description" not in df_mapped.columns
            ):
                # Check for common description column variations
                desc_variations = [
                    "desc",
                    "Desc",
                    "details",
                    "Details",
                    "memo",
                    "Memo",
                    "note",
                    "Note",
                    "narration",
                    "Narration",
                ]
                desc_found = False
                for desc_var in desc_variations:
                    if desc_var in df.columns:
                        df_mapped = df_mapped.rename(columns={desc_var: "Description"})
                        desc_found = True
                        break

                if not desc_found:
                    df_mapped["Description"] = ""

            st.success(f"✅ **Column mapping successful!**")
            col_info = []
            for standard, actual in found_columns.items():
                col_info.append(f"**{standard.title()}** ← {actual}")
            st.markdown("📋 **Mapped columns:** " + " | ".join(col_info))

            # Show preview
            st.subheader("👁️ Data Preview (After Column Mapping)")
            preview_df = df_mapped.head(10)
            st.dataframe(preview_df, use_container_width=True)  # Import to database
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("💾 Import to Database", type="primary"):
                    try:
                        # Use the mapped dataframe for import
                        df_import = df_mapped.copy()

                        # Convert column names to lowercase for database import
                        df_import.columns = df_import.columns.str.lower()                        # Import to database
                        imported_count = db.import_from_dataframe(df_import)
                        
                        if imported_count > 0:
                            st.success(
                                f"✅ Successfully imported {imported_count} records to database!"
                            )
                            # Clear the cached database to ensure fresh data loading
                            get_database.clear()
                            # Clear any filters to show all new data
                            if 'filters' in st.session_state:
                                st.session_state.filters = {
                                    "date_range": None,
                                    "categories": [],
                                    "amount_range": None,
                                }
                            st.rerun()
                        else:
                            st.warning("⚠️ No valid records found to import.")

                    except Exception as e:
                        st.error(f"❌ Error importing data: {str(e)}")

        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")


def show_manual_entry_section(db):
    """Show manual entry form with smart categorization"""
    st.subheader("✏️ Smart Manual Entry")

    # Get existing categories for dropdown
    existing_categories = db.get_categories()
    default_categories = [
        "Food",
        "Transportation",
        "Entertainment",
        "Utilities",
        "Healthcare",
        "Shopping",
        "Income",
        "Other",
    ]
    all_categories = list(set(existing_categories + default_categories))

    with st.form("expense_form", clear_on_submit=True):
        st.markdown("### Add New Expense/Income")

        col1, col2 = st.columns(2)

        with col1:
            entry_date = st.date_input(
                "📅 Date", value=date.today(), help="Select the date of the transaction"
            )

            amount = st.number_input(
                "💰 Amount",
                step=0.01,
                format="%.2f",
                help="Enter positive amount for income, negative for expenses",
            )

        with col2:
            # Smart category suggestion
            description = st.text_area(
                "📝 Description",
                placeholder="e.g., Whole Foods Market, Gas Station, Netflix subscription...",
                height=100,
                help="Enter a description - AI will suggest a category!",
            )

            # Auto-suggest category based on description
            suggested_category = ""
            if description and amount != 0:
                suggested_category = smart_expense_categorization(description, amount)
                if suggested_category != "Other":
                    st.info(f"🤖 **Smart Suggestion:** {suggested_category}")

            # Category selection with AI suggestion
            category_options = (
                ["Select existing..."]
                + sorted(all_categories)
                + ["➕ Add new category"]
            )

            # Pre-select suggested category if available
            default_index = 0
            if suggested_category and suggested_category in all_categories:
                default_index = category_options.index(suggested_category)

            category_option = st.selectbox(
                "📊 Category",
                options=category_options,
                index=default_index,
                help="AI-suggested category based on description, or choose your own",
            )

            if category_option == "➕ Add new category":
                category = st.text_input("Enter new category name:")
            elif category_option == "Select existing...":
                category = ""
            else:
                category = category_option

        # Advanced features
        with st.expander("🔬 Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                recurring = st.checkbox(
                    "🔄 Recurring Transaction",
                    help="Mark as a recurring expense/income",
                )
            with col2:
                important = st.checkbox(
                    "⭐ Important Transaction", help="Mark as important for tracking"
                )

        # Submit button
        submitted = st.form_submit_button("💾 Add Entry", type="primary")

        if submitted:
            # Validate inputs
            if not category or category == "Select existing...":
                st.error("❌ Please select or enter a category.")
                return

            if amount == 0:
                st.error("❌ Please enter a non-zero amount.")
                return

            try:
                # Insert into database
                expense_id = db.insert_expense(
                    date=entry_date.strftime("%Y-%m-%d"),
                    amount=amount,
                    category=category,
                    description=description,
                )

                transaction_type = "income" if amount > 0 else "expense"

                # Show success with smart insights
                success_msg = f"✅ Successfully added {transaction_type}: ${abs(amount):.2f} in {category}"
                if suggested_category and suggested_category == category:
                    success_msg += f" (AI suggestion used! 🤖)"

                st.success(success_msg)

                # Show additional insights for larger transactions
                if abs(amount) > 100:
                    if amount < 0:  # Expense
                        st.info(
                            f"💡 **Spending Insight:** This is a significant expense. Consider if it aligns with your budget goals."
                        )
                    else:  # Income
                        st.info(
                            f"💰 **Income Insight:** Great income addition! Consider allocating some to savings."
                        )

                st.rerun()

            except Exception as e:
                st.error(f"❌ Error adding entry: {str(e)}")


def show_expense_management_section(db):
    """Show expense management (view, edit, delete) with enhanced filtering"""
    st.subheader("📋 Expense Management")

    # Fetch all expenses
    expenses_df = db.fetch_expenses()

    if expenses_df.empty:
        st.info("📭 No expenses found. Add some entries to get started!")
        return

    # Add bulk actions header with delete all option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🔧 Bulk Actions")
    with col2:
        if st.button("🗑️ Delete All Data", type="secondary", key="manage_delete_all", help="⚠️ Permanently delete all data"):
            # Show confirmation
            st.warning("⚠️ **This will delete ALL expense data!** This action cannot be undone.")
            
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ Confirm Delete All", type="primary", key="manage_confirm_delete"):
                    try:
                        deleted_count = db.delete_all_data()
                        st.success(f"✅ Successfully deleted {deleted_count} records!")
                        # Clear cached data
                        get_database.clear()
                        if 'filters' in st.session_state:
                            st.session_state.filters = {
                                "date_range": None,
                                "categories": [],
                                "amount_range": None,
                            }
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting data: {str(e)}")
            
            with col_cancel:
                if st.button("❌ Cancel", key="manage_cancel_delete"):
                    st.rerun()

    st.markdown("---")

    # Apply filters
    filtered_df = apply_filters_to_dataframe(expenses_df, st.session_state.filters)

    # Display database stats
    stats = db.get_database_stats()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", stats["total_records"])
    with col2:
        st.metric("Total Expenses", f"${stats['total_expenses']:.2f}")
    with col3:
        st.metric("Total Income", f"${stats['total_income']:.2f}")
    with col4:
        st.metric("Net Savings", f"${stats['net_savings']:.2f}")

    # Show filter status
    if any(st.session_state.filters.values()):
        st.info(
            f"📊 Showing {len(filtered_df)} of {len(expenses_df)} records based on active filters"
        )

    # Display expenses table
    st.markdown("### 📊 Expense Records")

    if filtered_df.empty:
        st.warning(
            "⚠️ No records match the selected filters. Try adjusting your filter settings."
        )
        return

    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:.2f}")

    # Select columns to display
    display_columns = ["id", "date", "amount", "category", "description"]
    display_df = display_df[display_columns]

    # Display with selection
    selected_indices = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun",
    )

    # Edit/Delete functionality
    if selected_indices and len(selected_indices.selection.rows) > 0:
        selected_row_idx = selected_indices.selection.rows[0]
        selected_expense_id = filtered_df.iloc[selected_row_idx]["id"]
        selected_expense = db.get_expense_by_id(selected_expense_id)

        if selected_expense:
            st.markdown("### ✏️ Edit Selected Expense")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Edit Entry", type="secondary"):
                    st.session_state.editing_expense = selected_expense

            with col2:
                if st.button("🗑️ Delete Entry", type="primary"):
                    if db.delete_expense(selected_expense_id):
                        st.success("✅ Expense deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete expense.")

    # Edit form
    if st.session_state.editing_expense:
        expense = st.session_state.editing_expense

        st.markdown("### 📝 Edit Expense")

        with st.form("edit_expense_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_date = st.date_input(
                    "Date", value=datetime.strptime(expense["date"], "%Y-%m-%d").date()
                )

                edit_amount = st.number_input(
                    "Amount", value=float(expense["amount"]), step=0.01, format="%.2f"
                )

            with col2:
                categories = db.get_categories()
                current_category = expense["category"]

                if current_category in categories:
                    category_index = categories.index(current_category)
                else:
                    categories.append(current_category)
                    category_index = len(categories) - 1

                edit_category = st.selectbox(
                    "Category", options=categories, index=category_index
                )

            edit_description = st.text_area(
                "Description", value=expense["description"] or ""
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    try:
                        success = db.update_expense(
                            expense_id=expense["id"],
                            date=edit_date.strftime("%Y-%m-%d"),
                            amount=edit_amount,
                            category=edit_category,
                            description=edit_description,
                        )

                        if success:
                            st.success("✅ Expense updated successfully!")
                            st.session_state.editing_expense = None
                            st.rerun()
                        else:
                            st.error("❌ Failed to update expense.")

                    except Exception as e:
                        st.error(f"❌ Error updating expense: {str(e)}")

            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.editing_expense = None
                    st.rerun()


def show_analytics_section(db):
    """Show enhanced analytics and visualizations with Plotly"""
    st.subheader("📊 Interactive Analytics Dashboard")

    # Fetch all expenses
    expenses_df = db.fetch_expenses()

    if expenses_df.empty:
        st.info("📭 No data available for analysis. Add some expenses first!")
        return

    # Apply filters
    filtered_df = apply_filters_to_dataframe(expenses_df, st.session_state.filters)

    if filtered_df.empty:
        st.warning(
            "⚠️ No data matches the current filters. Try adjusting your filter settings."
        )
        return

    # Show filter status
    if any(st.session_state.filters.values()):
        st.info(
            f"📊 Showing {len(filtered_df)} of {len(expenses_df)} records based on active filters"
        )    # Convert to format expected by analyzer
    df_analysis = filtered_df.copy()
    
    # Debug info for troubleshooting
    with st.expander("🔍 Debug Info (Expand if analytics not working)"):
        st.write(f"**Original DataFrame shape:** {filtered_df.shape}")
        st.write(f"**Original columns:** {list(filtered_df.columns)}")
        st.write(f"**Data types:** {filtered_df.dtypes.to_dict()}")
        
        if not filtered_df.empty:
            st.write("**Sample data:**")
            st.dataframe(filtered_df.head(3))

    # Ensure proper column format for analyzer
    df_analysis.columns = df_analysis.columns.str.title()
    
    # Handle date conversion properly
    if 'Date' in df_analysis.columns:
        try:
            if df_analysis['Date'].dtype == 'object':
                df_analysis['Date'] = pd.to_datetime(df_analysis['Date'])
            df_analysis["Date"] = df_analysis["Date"].dt.strftime("%Y-%m-%d")
        except Exception as e:
            st.error(f"Date conversion error: {e}")
            st.write("Date column sample:", df_analysis['Date'].head())
    
    # Ensure Amount is numeric
    if 'Amount' in df_analysis.columns:
        df_analysis['Amount'] = pd.to_numeric(df_analysis['Amount'], errors='coerce')

    try:
        # Category analysis
        category_summary = analyze_expenses_by_category(df_analysis)

        if not category_summary.empty:
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(
                ["📊 Overview", "📈 Trends", "🔍 Details", "⚖️ Compare"]
            )

            with tab1:
                # Overview charts
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("� Expenses by Category")
                    bar_fig = create_interactive_bar_chart(
                        category_summary, "Interactive Spending by Category"
                    )
                    st.plotly_chart(bar_fig, use_container_width=True)

                with col2:
                    st.subheader("🥧 Expense Distribution")
                    pie_fig = create_interactive_pie_chart(
                        category_summary, "Interactive Expense Distribution"
                    )
                    st.plotly_chart(pie_fig, use_container_width=True)

                # Monthly trend
                monthly_trend = analyze_monthly_trend(df_analysis)

                if not monthly_trend.empty:
                    st.subheader("📈 Monthly Expense Trend")
                    line_fig = create_interactive_line_chart(
                        monthly_trend, "Interactive Monthly Trend"
                    )
                    st.plotly_chart(line_fig, use_container_width=True)

            with tab2:
                # Detailed trend analysis
                st.subheader("📅 Time-based Analysis")

                # Monthly trend with more details
                if not monthly_trend.empty:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Highest Month",
                            monthly_trend.idxmax(),
                            f"${monthly_trend.max():.2f}",
                        )

                    with col2:
                        st.metric(
                            "Lowest Month",
                            monthly_trend.idxmin(),
                            f"${monthly_trend.min():.2f}",
                        )

                    # Trend line chart
                    line_fig = create_interactive_line_chart(
                        monthly_trend, "Detailed Monthly Analysis", show_trend_line=True
                    )
                    st.plotly_chart(line_fig, use_container_width=True)

                    # Monthly statistics
                    st.subheader("📊 Monthly Statistics")
                    avg_monthly = monthly_trend.mean()
                    std_monthly = monthly_trend.std()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Monthly", f"${avg_monthly:.2f}")
                    with col2:
                        st.metric("Std Deviation", f"${std_monthly:.2f}")
                    with col3:
                        growth_rate = (
                            (
                                (monthly_trend.iloc[-1] - monthly_trend.iloc[0])
                                / monthly_trend.iloc[0]
                                * 100
                            )
                            if len(monthly_trend) > 1
                            else 0
                        )
                        st.metric("Growth Rate", f"{growth_rate:.1f}%")

            with tab3:
                # Detailed breakdown
                st.subheader("🔍 Detailed Category Breakdown")

                # Top categories table
                top_categories = category_summary.head(10)

                # Create detailed table
                detail_data = []
                total_expenses = category_summary.sum()

                for category, amount in top_categories.items():
                    percentage = (amount / total_expenses) * 100
                    detail_data.append(
                        {
                            "Category": category,
                            "Amount": f"${amount:.2f}",
                            "Percentage": f"{percentage:.1f}%",
                        }
                    )

                detail_df = pd.DataFrame(detail_data)
                st.dataframe(detail_df, use_container_width=True, hide_index=True)

                # Category insights
                st.subheader("💡 Category Insights")
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Top Spending Categories:**")
                    for i, (cat, amount) in enumerate(
                        top_categories.head(3).items(), 1
                    ):
                        st.write(f"{i}. {cat}: ${amount:.2f}")

                with col2:
                    st.write("**Spending Distribution:**")
                    top_3_pct = top_categories.head(3).sum() / total_expenses * 100
                    st.write(f"• Top 3 categories: {top_3_pct:.1f}% of total")
                    st.write(f"• Total categories: {len(category_summary)}")
                    st.write(
                        f"• Average per category: ${total_expenses / len(category_summary):.2f}"
                    )

            with tab4:
                # Category comparison
                st.subheader("⚖️ Category Comparison")

                categories = list(category_summary.index)
                selected_for_comparison = st.multiselect(
                    "Select categories to compare over time:",
                    options=categories,
                    default=categories[:3] if len(categories) >= 3 else categories,
                    key="comparison_categories",
                )

                if selected_for_comparison:
                    comparison_fig = create_category_comparison(
                        df_analysis, selected_for_comparison
                    )
                    st.plotly_chart(comparison_fig, use_container_width=True)

                    # Comparison insights
                    st.subheader("📋 Comparison Insights")
                    comparison_data = []

                    for category in selected_for_comparison:
                        cat_amount = category_summary.get(category, 0)
                        comparison_data.append(
                            {
                                "Category": category,
                                "Total Amount": f"${cat_amount:.2f}",
                                "Percentage of Total": f"{(cat_amount / category_summary.sum() * 100):.1f}%",
                            }
                        )

                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(
                        comparison_df, use_container_width=True, hide_index=True
                    )

            # Summary report at the bottom
            st.markdown("---")
            st.subheader("📋 Summary Report")
            report = generate_expense_summary_report(df_analysis)

            if "error" not in report:
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Expenses", f"${report['total_expenses']:.2f}")
                    st.metric("Top Category", report["top_expense_category"])

                with col2:
                    st.metric("Total Income", f"${report['total_income']:.2f}")
                    st.metric("Categories", report["categories_count"])

                with col3:
                    st.metric("Net Savings", f"${report['net_savings']:.2f}")
                    savings_rate = (
                        (report["net_savings"] / report["total_income"] * 100)
                        if report["total_income"] > 0
                        else 0
                    )
                    st.metric("Savings Rate", f"{savings_rate:.1f}%")

                with col4:
                    st.metric("Avg Monthly", f"${report['avg_monthly_expense']:.2f}")
                    st.metric("Months Covered", report["months_covered"])

        else:
            st.warning("⚠️ No expense data found in the selected time period.")

    except Exception as e:
        st.error(f"❌ Error generating analytics: {str(e)}")
        st.info("💡 Tip: Check if your data contains valid dates and amounts.")


def show_ai_assistant_section(db):
    """Show Enhanced AI Assistant with Advanced NLP and Financial Intelligence"""
    st.subheader("🤖 Advanced AI Financial Advisor")

    # AI Mode Selection
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🧠 Choose Your AI Experience")
    with col2:
        ai_mode = st.selectbox(
            "AI Mode:",
            ["🚀 Advanced Mode", "📝 Basic Mode"],
            key="ai_mode_selector",
            help="Advanced Mode uses enhanced NLP and financial intelligence",
        )

    # Check Ollama status
    is_available, status_msg = check_ollama_status()

    if not is_available:
        st.warning(f"⚠️ **AI Assistant Setup Required**\n\n{status_msg}")

        with st.expander("🛠️ Setup Instructions"):
            st.markdown(
                """
            **To use the AI Assistant, you need to set up Ollama:**
            
            1. **Install Ollama:** Visit [ollama.ai](https://ollama.ai) and download for your system
            
            2. **Start Ollama service:**
               ```bash
               ollama serve
               ```
            
            3. **Install AI models:**
               ```bash
               ollama pull mistral
               ollama pull llama3
               ```
            
            4. **Verify installation:**
               ```bash
               ollama list
               ```
            
            5. **Refresh this page** after setup is complete
            
            💡 **Note:** All AI processing happens locally on your machine for complete privacy!
            """
            )
        return

    # Show AI capabilities based on mode
    if ai_mode == "🚀 Advanced Mode":
        st.success(f"✅ {status_msg} - Advanced NLP & Financial Intelligence Enabled")

        # Advanced AI capabilities info
        with st.expander("🔬 Advanced AI Capabilities"):
            st.markdown(
                """
            **🧠 Enhanced NLP Features:**
            - Intent recognition and context understanding
            - Financial domain expertise and terminology
            - Predictive analytics and trend forecasting  
            - Personalized budgeting recommendations
            - Behavioral spending pattern analysis
            - Smart expense categorization
            
            **📊 Advanced Analysis:**
            - Temporal spending patterns
            - Budget optimization insights
            - Cash flow predictions
            - Financial health scoring
            - Comparative benchmarking
            - Goal-based planning advice
            """
            )
    else:
        st.success(f"✅ {status_msg} - Basic Mode")

    # Fetch expenses for context
    expenses_df = db.fetch_expenses()

    if expenses_df.empty:
        st.info(
            "📭 Add some expense data first to start chatting with the AI assistant!"
        )
        return

    # Apply filters to get current data context
    filtered_df = apply_filters_to_dataframe(expenses_df, st.session_state.filters)

    # Model selection
    col1, col2 = st.columns([2, 1])

    with col1:
        if ai_mode == "🚀 Advanced Mode":
            st.markdown("### 🎯 Advanced Financial Analysis")
        else:
            st.markdown("### 💬 Basic Financial Chat")

    with col2:
        available_models = get_available_models()
        if "mistral" in available_models and "llama3" in available_models:
            model_options = ["mistral", "llama3"]
        else:
            model_options = (
                available_models[:2] if len(available_models) >= 2 else available_models
            )

        if model_options:
            selected_model = st.selectbox(
                "🧠 AI Model:",
                options=model_options,
                index=(
                    model_options.index(st.session_state.preferred_ai_model)
                    if st.session_state.preferred_ai_model in model_options
                    else 0
                ),
                key="ai_model_selector",
            )
            st.session_state.preferred_ai_model = selected_model
        else:
            st.error("No AI models available. Please install mistral or llama3.")
            return

    # Show current data context summary
    if any(st.session_state.filters.values()):
        st.info(
            f"🔍 AI will analyze {len(filtered_df)} filtered records from your expense data"
        )
    else:
        st.info(
            f"📊 AI will analyze all {len(filtered_df)} records from your expense data"
        )

    # Enhanced chat interface for Advanced Mode
    if ai_mode == "🚀 Advanced Mode":
        # Advanced query categories
        st.markdown("#### 🎯 Quick Analysis Categories")
        analysis_cols = st.columns(4)

        with analysis_cols[0]:
            if st.button("📊 Spending Patterns", key="pattern_analysis"):
                st.session_state.last_query = "Analyze my spending patterns and identify trends. What behavioral insights can you provide?"
                st.rerun()

        with analysis_cols[1]:
            if st.button("🔮 Future Predictions", key="prediction_analysis"):
                st.session_state.last_query = "Predict my future spending trends and provide forecasting insights for next month."
                st.rerun()

        with analysis_cols[2]:
            if st.button("💰 Budget Optimization", key="budget_analysis"):
                st.session_state.last_query = "Analyze my budget allocation and provide optimization recommendations based on financial best practices."
                st.rerun()

        with analysis_cols[3]:
            if st.button("🎯 Financial Goals", key="goal_analysis"):
                st.session_state.last_query = "Help me set realistic financial goals based on my current spending patterns and suggest actionable steps."
                st.rerun()

    # Chat interface
    col1, col2 = st.columns([4, 1])

    with col1:
        if ai_mode == "🚀 Advanced Mode":
            user_query = st.text_area(
                "Ask your advanced financial question:",
                placeholder="e.g., Analyze my spending behavior and predict next month's expenses with budget recommendations...",
                key="ai_query_input",
                value=st.session_state.last_query,
                height=100,
            )
        else:
            user_query = st.text_input(
                "Ask me anything about your expenses:",
                placeholder="e.g., How much did I spend on food last month?",
                key="ai_query_input_basic",
                value=st.session_state.last_query,
            )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button(
            "🚀 Analyze" if ai_mode == "🚀 Advanced Mode" else "💬 Ask",
            type="primary",
            key="ask_ai_button",
        )

    # Example questions based on mode
    if ai_mode == "🚀 Advanced Mode":
        st.markdown("💡 **Advanced Analysis Examples:**")
        example_cols = st.columns(2)

        with example_cols[0]:
            if st.button("🔍 Deep Spending Analysis", key="advanced_example1"):
                st.session_state.last_query = "Provide a comprehensive analysis of my spending behavior, identify patterns, and give personalized recommendations for optimization."
                st.rerun()

        with example_cols[1]:
            if st.button("📈 Predictive Financial Planning", key="advanced_example2"):
                st.session_state.last_query = "Based on my historical data, predict my financial trends and create a strategic plan for better money management."
                st.rerun()
    else:
        st.markdown("💡 **Basic Questions:**")
        example_cols = st.columns(3)

        with example_cols[0]:
            if st.button("💰 Biggest expense category?", key="basic_example1"):
                st.session_state.last_query = "What's my biggest expense category?"
                st.rerun()

        with example_cols[1]:
            if st.button("📈 Spending trends?", key="basic_example2"):
                st.session_state.last_query = "How are my spending trends over time?"
                st.rerun()

        with example_cols[2]:
            if st.button("💡 Budgeting advice?", key="basic_example3"):
                st.session_state.last_query = (
                    "Give me budgeting advice based on my spending patterns"
                )
                st.rerun()

    # Process AI query
    if (ask_button or user_query != st.session_state.last_query) and user_query:
        st.session_state.last_query = user_query

        # Show thinking spinner with mode-specific message
        thinking_message = (
            f"🧠 {selected_model} is performing advanced financial analysis..."
            if ai_mode == "🚀 Advanced Mode"
            else f"🤔 {selected_model} is analyzing your expenses..."
        )

        with st.spinner(thinking_message):
            if ai_mode == "🚀 Advanced Mode":
                # Use advanced AI with NLP and financial intelligence
                ai_response, used_model = advanced_query_expense_ai(
                    user_query, filtered_df, selected_model
                )
            else:
                # Use basic AI
                context = get_expense_context(filtered_df, st.session_state.filters)
                ai_response, used_model = query_expense_ai(
                    user_query, context, selected_model
                )

        # Display response
        if used_model:
            # Successful response
            if used_model != selected_model:
                st.warning(
                    f"⚠️ Primary model {selected_model} failed, used {used_model} instead"
                )

            mode_icon = "🧠" if ai_mode == "🚀 Advanced Mode" else "🤖"
            st.markdown(
                f"### {mode_icon} **AI Response** ({used_model} - {ai_mode.split()[0]})"
            )
            st.markdown(ai_response)

            # Add to chat history
            chat_entry = {
                "query": user_query,
                "response": ai_response,
                "model": used_model,
                "mode": ai_mode,
                "timestamp": datetime.now(),
            }
            st.session_state.ai_chat_history.append(chat_entry)

            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 3])
            with col1:
                if st.button("🔄 Try Again", key="try_again_button"):
                    st.rerun()
            with col2:
                if st.button("💾 Save Analysis", key="save_analysis"):
                    st.success("Analysis saved to chat history!")
        else:
            # Error occurred
            st.error("❌ **AI Assistant Error**")
            st.markdown(ai_response)

            # Try again button for errors
            if st.button("🔄 Try Again", key="error_try_again"):
                st.rerun()

    # Enhanced Chat history
    if st.session_state.ai_chat_history:
        st.markdown("---")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📜 Analysis History")
        with col2:
            if st.button("🗑️ Clear History", key="clear_chat_history"):
                st.session_state.ai_chat_history = []
                st.rerun()

        # Show recent chats with mode indicators
        recent_chats = st.session_state.ai_chat_history[-5:]

        for i, chat in enumerate(reversed(recent_chats)):
            mode_emoji = "🧠" if "Advanced" in chat.get("mode", "") else "💬"
            with st.expander(f"{mode_emoji} {chat['query'][:60]}... ({chat['model']})"):
                st.markdown(f"**Question:** {chat['query']}")
                st.markdown(f"**Answer:** {chat['response']}")
                st.caption(
                    f"Model: {chat['model']} • Mode: {chat.get('mode', 'Basic')} • {chat['timestamp'].strftime('%Y-%m-%d %H:%M')}"
                )


def main():
    # Header
    st.markdown('<h1 class="main-header">💰 LocalBudgetAI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Your Privacy-First Budget & Expense Analyzer</p>',
        unsafe_allow_html=True,
    )

    # Initialize database
    db = get_database()

    # Create enhanced sidebar with filters
    page = create_sidebar_filters(db)

    # Main content based on navigation
    if page == "📊 Dashboard":
        st.markdown("## 🏠 Interactive Dashboard")        # Quick stats
        stats = db.get_database_stats()

        # Add Delete Data button in the dashboard
        if stats["total_records"] > 0:
            st.markdown("### 🗑️ Data Management")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.info(f"📊 Database contains {stats['total_records']} records")
            
            with col2:
                if st.button("🗑️ Delete All Data", type="secondary", help="⚠️ This will permanently delete all your data!"):
                    # Show confirmation dialog
                    if 'confirm_delete' not in st.session_state:
                        st.session_state.confirm_delete = False
                    
                    if not st.session_state.confirm_delete:
                        st.session_state.confirm_delete = True
                        st.warning("⚠️ **Are you sure?** This action cannot be undone!")
                        
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("✅ Yes, Delete All", type="primary", key="confirm_yes"):
                                try:
                                    deleted_count = db.delete_all_data()
                                    st.success(f"✅ Successfully deleted {deleted_count} records!")
                                    st.session_state.confirm_delete = False
                                    # Clear any cached data
                                    if 'filters' in st.session_state:
                                        st.session_state.filters = {
                                            "date_range": None,
                                            "categories": [],
                                            "amount_range": None,
                                        }
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting data: {str(e)}")
                        
                        with col_no:
                            if st.button("❌ Cancel", key="confirm_no"):
                                st.session_state.confirm_delete = False
                                st.rerun()
                    
            st.markdown("---")

        if stats["total_records"] > 0:
            # Get filtered data for dashboard
            expenses_df = db.fetch_expenses()
            filtered_df = apply_filters_to_dataframe(
                expenses_df, st.session_state.filters
            )

            # Show filter status
            if any(st.session_state.filters.values()):
                st.info(
                    f"📊 Showing {len(filtered_df)} of {len(expenses_df)} records based on active filters"
                )

            # Quick stats with filtered data
            if not filtered_df.empty:
                # Calculate filtered stats
                expenses_only = filtered_df[filtered_df["amount"] < 0]
                income_only = filtered_df[filtered_df["amount"] > 0]

                filtered_total_expenses = (
                    expenses_only["amount"].abs().sum()
                    if not expenses_only.empty
                    else 0
                )
                filtered_total_income = (
                    income_only["amount"].sum() if not income_only.empty else 0
                )
                filtered_net_savings = filtered_total_income - filtered_total_expenses

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Filtered Records",
                        len(filtered_df),
                        delta=len(filtered_df) - stats["total_records"],
                    )
                with col2:
                    st.metric(
                        "Filtered Expenses",
                        f"${filtered_total_expenses:.2f}",
                        delta=f"${filtered_total_expenses - stats['total_expenses']:.2f}",
                    )
                with col3:
                    st.metric(
                        "Filtered Income",
                        f"${filtered_total_income:.2f}",
                        delta=f"${filtered_total_income - stats['total_income']:.2f}",
                    )
                with col4:
                    st.metric(
                        "Filtered Net Savings",
                        f"${filtered_net_savings:.2f}",
                        delta=f"${filtered_net_savings - stats['net_savings']:.2f}",
                    )

                # Dashboard overview chart
                if len(filtered_df) > 0:
                    # Convert to analyzer format
                    df_analysis = filtered_df.copy()
                    df_analysis.columns = df_analysis.columns.str.title()
                    df_analysis["Date"] = df_analysis["Date"].dt.strftime("%Y-%m-%d")

                    st.subheader("📊 Dashboard Overview")
                    dashboard_fig = create_dashboard_overview(df_analysis)
                    st.plotly_chart(dashboard_fig, use_container_width=True)

                # Recent transactions
                st.markdown("### 🕐 Recent Transactions")
                recent_df = filtered_df.head(10)

                if not recent_df.empty:
                    display_df = recent_df.copy()
                    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
                    display_df["amount"] = display_df["amount"].apply(
                        lambda x: f"${x:.2f}"
                    )
                    st.dataframe(
                        display_df[["date", "amount", "category", "description"]],
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.warning(
                    "⚠️ No data matches your current filters. Try adjusting the filter settings."
                )
        else:
            st.markdown(
                """
            <div class="upload-section">
                <h3>🚀 Welcome to LocalBudgetAI!</h3>
                <p>Get started by adding your first expense or uploading a CSV file.</p>
                <p>Use the navigation menu to explore different features.</p>
                <p>💡 <strong>New:</strong> Use the sidebar filters to analyze specific time periods and categories!</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    elif page == "📁 Data Input":
        st.markdown("## 📁 Data Input")

        # Dual input option
        input_method = st.radio(
            "Choose input method:",
            ["📁 Upload CSV", "✏️ Manual Entry"],
            horizontal=True,
            key="input_method",
        )

        if input_method == "📁 Upload CSV":
            show_csv_upload_section(db)
        else:
            show_manual_entry_section(db)

    elif page == "📋 Manage Expenses":
        show_expense_management_section(db)

    elif page == "📈 Analytics":
        show_analytics_section(db)

    elif page == "🤖 AI Assistant":
        show_ai_assistant_section(db)

    elif page == "🤖 AI Assistant":
        show_ai_assistant_section(db)


if __name__ == "__main__":
    main()
