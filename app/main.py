import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import ExpenseDatabase
from analyzer import (analyze_expenses_by_category, plot_expense_bar_chart, 
                     plot_expense_pie_chart, analyze_monthly_trend, 
                     plot_monthly_trend, generate_expense_summary_report)

# Configure page
st.set_page_config(
    page_title="LocalBudgetAI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
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
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    """Initialize and return the database connection."""
    return ExpenseDatabase()

def validate_required_columns(df):
    """Validate that the uploaded CSV contains required columns"""
    required_columns = ['Date', 'Amount', 'Category']
    missing_columns = []
    
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    return missing_columns

def show_csv_upload_section(db):
    """Show CSV upload section"""
    st.subheader("📁 Upload CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file containing your transaction data",
        type=['csv'],
        help="Upload your transaction data in CSV format. Expected columns: Date, Amount, Category"
    )
    
    if uploaded_file is not None:
        try:
            # Load the CSV file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! Loaded {len(df)} records.")
            
            # Validate required columns
            missing_columns = validate_required_columns(df)
            
            if missing_columns:
                st.markdown(f"""
                <div class="error-box">
                    <h4>⚠️ Missing Required Columns</h4>
                    <p>The following required columns are missing from your CSV:</p>
                    <ul>
                        {''.join([f'<li><strong>{col}</strong></li>' for col in missing_columns])}
                    </ul>
                    <p>Please ensure your CSV contains columns: <strong>Date</strong>, <strong>Amount</strong>, and <strong>Category</strong></p>
                </div>
                """, unsafe_allow_html=True)
                return
            
            # Show preview
            st.subheader("👁️ Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Import to database
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("💾 Import to Database", type="primary"):
                    try:
                        # Standardize column names
                        df_import = df.copy()
                        df_import.columns = df_import.columns.str.title()
                        
                        # Ensure required columns exist
                        if 'Description' not in df_import.columns:
                            df_import['Description'] = ''
                        
                        # Import to database
                        imported_count = db.import_from_dataframe(df_import)
                        
                        if imported_count > 0:
                            st.success(f"✅ Successfully imported {imported_count} records to database!")
                            st.rerun()
                        else:
                            st.warning("⚠️ No valid records found to import.")
                            
                    except Exception as e:
                        st.error(f"❌ Error importing data: {str(e)}")
            
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")

def show_manual_entry_section(db):
    """Show manual entry form"""
    st.subheader("✏️ Manual Entry")
    
    # Get existing categories for dropdown
    existing_categories = db.get_categories()
    default_categories = ['Food', 'Transportation', 'Entertainment', 'Utilities', 
                         'Healthcare', 'Shopping', 'Income', 'Other']
    all_categories = list(set(existing_categories + default_categories))
    
    with st.form("expense_form", clear_on_submit=True):
        st.markdown("### Add New Expense/Income")
        
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input(
                "📅 Date",
                value=date.today(),
                help="Select the date of the transaction"
            )
            
            amount = st.number_input(
                "💰 Amount",
                step=0.01,
                format="%.2f",
                help="Enter positive amount for income, negative for expenses"
            )
        
        with col2:
            # Category selection with option to add new
            category_option = st.selectbox(
                "📊 Category",
                options=["Select existing..."] + sorted(all_categories) + ["➕ Add new category"],
                help="Choose a category or add a new one"
            )
            
            if category_option == "➕ Add new category":
                category = st.text_input("Enter new category name:")
            elif category_option == "Select existing...":
                category = ""
            else:
                category = category_option
        
        description = st.text_area(
            "📝 Description (Optional)",
            placeholder="Add a description for this transaction...",
            height=100
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
                    date=entry_date.strftime('%Y-%m-%d'),
                    amount=amount,
                    category=category,
                    description=description
                )
                
                transaction_type = "income" if amount > 0 else "expense"
                st.success(f"✅ Successfully added {transaction_type}: ${abs(amount):.2f} in {category}")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error adding entry: {str(e)}")

def show_expense_management_section(db):
    """Show expense management (view, edit, delete)"""
    st.subheader("📋 Expense Management")
    
    # Fetch all expenses
    expenses_df = db.fetch_expenses()
    
    if expenses_df.empty:
        st.info("📭 No expenses found. Add some entries to get started!")
        return
    
    # Display database stats
    stats = db.get_database_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", stats['total_records'])
    with col2:
        st.metric("Total Expenses", f"${stats['total_expenses']:.2f}")
    with col3:
        st.metric("Total Income", f"${stats['total_income']:.2f}")
    with col4:
        st.metric("Net Savings", f"${stats['net_savings']:.2f}")
    
    # Filters
    st.markdown("### 🔍 Filters")
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        categories = db.get_categories()
        selected_category = st.selectbox(
            "Category",
            options=["All"] + categories,
            key="filter_category"
        )
    
    with filter_col2:
        start_date = st.date_input("Start Date", key="filter_start")
    
    with filter_col3:
        end_date = st.date_input("End Date", key="filter_end")
    
    # Apply filters
    filtered_df = expenses_df.copy()
    
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    if start_date:
        filtered_df = filtered_df[filtered_df['date'] >= pd.to_datetime(start_date)]
    
    if end_date:
        filtered_df = filtered_df[filtered_df['date'] <= pd.to_datetime(end_date)]
    
    # Display expenses table
    st.markdown("### 📊 Expense Records")
    
    if filtered_df.empty:
        st.info("No records match the selected filters.")
        return
    
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
    
    # Select columns to display
    display_columns = ['id', 'date', 'amount', 'category', 'description']
    display_df = display_df[display_columns]
    
    # Display with selection
    selected_indices = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        selection_mode="single-row",
        on_select="rerun"
    )
    
    # Edit/Delete functionality
    if selected_indices and len(selected_indices.selection.rows) > 0:
        selected_row_idx = selected_indices.selection.rows[0]
        selected_expense_id = filtered_df.iloc[selected_row_idx]['id']
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
    if 'editing_expense' in st.session_state:
        expense = st.session_state.editing_expense
        
        st.markdown("### 📝 Edit Expense")
        
        with st.form("edit_expense_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_date = st.date_input(
                    "Date",
                    value=datetime.strptime(expense['date'], '%Y-%m-%d').date()
                )
                
                edit_amount = st.number_input(
                    "Amount",
                    value=float(expense['amount']),
                    step=0.01,
                    format="%.2f"
                )
            
            with col2:
                categories = db.get_categories()
                current_category = expense['category']
                
                if current_category in categories:
                    category_index = categories.index(current_category)
                else:
                    categories.append(current_category)
                    category_index = len(categories) - 1
                
                edit_category = st.selectbox(
                    "Category",
                    options=categories,
                    index=category_index
                )
            
            edit_description = st.text_area(
                "Description",
                value=expense['description'] or ""
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    try:
                        success = db.update_expense(
                            expense_id=expense['id'],
                            date=edit_date.strftime('%Y-%m-%d'),
                            amount=edit_amount,
                            category=edit_category,
                            description=edit_description
                        )
                        
                        if success:
                            st.success("✅ Expense updated successfully!")
                            del st.session_state.editing_expense
                            st.rerun()
                        else:
                            st.error("❌ Failed to update expense.")
                    
                    except Exception as e:
                        st.error(f"❌ Error updating expense: {str(e)}")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    del st.session_state.editing_expense
                    st.rerun()

def show_analytics_section(db):
    """Show analytics and visualizations"""
    st.subheader("📊 Analytics Dashboard")
    
    # Fetch all expenses
    expenses_df = db.fetch_expenses()
    
    if expenses_df.empty:
        st.info("📭 No data available for analysis. Add some expenses first!")
        return
    
    # Convert to format expected by analyzer
    df_analysis = expenses_df.copy()
    df_analysis.columns = df_analysis.columns.str.title()
    df_analysis['Date'] = df_analysis['Date'].dt.strftime('%Y-%m-%d')
    
    try:
        # Category analysis
        category_summary = analyze_expenses_by_category(df_analysis)
        
        if not category_summary.empty:
            # Display charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Expenses by Category")
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                plot_expense_bar_chart(category_summary, ax=ax1)
                st.pyplot(fig1)
            
            with col2:
                st.markdown("#### 🥧 Expense Distribution")
                fig2, ax2 = plt.subplots(figsize=(8, 8))
                plot_expense_pie_chart(category_summary, ax=ax2)
                st.pyplot(fig2)
            
            # Monthly trend
            monthly_trend = analyze_monthly_trend(df_analysis)
            
            if not monthly_trend.empty:
                st.markdown("#### 📈 Monthly Trend")
                fig3, ax3 = plt.subplots(figsize=(12, 6))
                plot_monthly_trend(monthly_trend, ax=ax3)
                st.pyplot(fig3)
            
            # Summary report
            st.markdown("#### 📋 Summary Report")
            report = generate_expense_summary_report(df_analysis)
            
            if 'error' not in report:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Expenses", f"${report['total_expenses']:.2f}")
                    st.metric("Top Category", report['top_expense_category'])
                
                with col2:
                    st.metric("Total Income", f"${report['total_income']:.2f}")
                    st.metric("Categories", report['categories_count'])
                
                with col3:
                    st.metric("Net Savings", f"${report['net_savings']:.2f}")
                    savings_rate = (report['net_savings'] / report['total_income'] * 100) if report['total_income'] > 0 else 0
                    st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    except Exception as e:
        st.error(f"❌ Error generating analytics: {str(e)}")

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 LocalBudgetAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Privacy-First Budget & Expense Analyzer</p>', unsafe_allow_html=True)
    
    # Initialize database
    db = get_database()
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    page = st.sidebar.radio(
        "Choose a section:",
        ["📊 Dashboard", "📁 Data Input", "📋 Manage Expenses", "📈 Analytics"],
        key="navigation"
    )
    
    if page == "📊 Dashboard":
        st.markdown("## 🏠 Dashboard")
        
        # Quick stats
        stats = db.get_database_stats()
        
        if stats['total_records'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", stats['total_records'])
            with col2:
                st.metric("Total Expenses", f"${stats['total_expenses']:.2f}")
            with col3:
                st.metric("Total Income", f"${stats['total_income']:.2f}")
            with col4:
                st.metric("Net Savings", f"${stats['net_savings']:.2f}")
            
            # Recent transactions
            st.markdown("### 🕐 Recent Transactions")
            recent_df = db.fetch_expenses(limit=10)
            
            if not recent_df.empty:
                display_df = recent_df.copy()
                display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
                display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:.2f}")
                st.dataframe(display_df[['date', 'amount', 'category', 'description']], 
                           use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            <div class="upload-section">
                <h3>🚀 Welcome to LocalBudgetAI!</h3>
                <p>Get started by adding your first expense or uploading a CSV file.</p>
                <p>Use the navigation menu to explore different features.</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "📁 Data Input":
        st.markdown("## 📁 Data Input")
        
        # Dual input option
        input_method = st.radio(
            "Choose input method:",
            ["📁 Upload CSV", "✏️ Manual Entry"],
            horizontal=True,
            key="input_method"
        )
        
        if input_method == "📁 Upload CSV":
            show_csv_upload_section(db)
        else:
            show_manual_entry_section(db)
    
    elif page == "📋 Manage Expenses":
        show_expense_management_section(db)
    
    elif page == "📈 Analytics":
        show_analytics_section(db)

if __name__ == "__main__":
    main()
