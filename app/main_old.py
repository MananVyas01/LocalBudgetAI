import streamlit as st
import pandas as pd
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

def validate_required_columns(df):
    """
    Validate that the uploaded CSV contains required columns
    """
    required_columns = ['Date', 'Amount', 'Category']
    missing_columns = []
    
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    
    return missing_columns

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 LocalBudgetAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Privacy-First Budget & Expense Analyzer</p>', unsafe_allow_html=True)
    
    # Description
    st.markdown("""
    Welcome to LocalBudgetAI! This application helps you analyze your budget and expenses 
    while keeping all your data private and local. Simply upload your CSV file to get started.
    """)
    
    st.markdown("---")
    
    # File upload section
    st.subheader("📁 Upload Your CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file containing your transaction data",
        type=['csv'],
        help="Upload your transaction data in CSV format. Expected columns: Date, Amount, Category"
    )
    
    # Handle file upload
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
            else:
                st.markdown("""
                <div class="success-box">
                    <h4>✅ All Required Columns Found</h4>
                    <p>Your CSV file contains all the required columns. Great!</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display basic file information
            st.subheader("� File Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            # Display column information
            st.subheader("📋 Column Information")
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes.values,
                'Non-Null Count': df.count().values,
                'Null Count': df.isnull().sum().values
            })
            st.dataframe(col_info, use_container_width=True)
            
            # Display first 5 rows
            st.subheader("👁️ First 5 Rows of Your Data")
            st.dataframe(df.head(), use_container_width=True)
            
            # Show sample of data for verification
            if len(df) > 5:
                st.info(f"Showing first 5 rows out of {len(df)} total records. Your data looks good!")
            
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")
    
    else:
        # Welcome screen when no file is uploaded
        st.markdown("""
        <div class="upload-section">
            <h3>🚀 Get Started</h3>
            <p>Upload your CSV file above to begin analyzing your budget data!</p>
            <br>
            <h4>📋 Expected CSV Format</h4>
            <p>Your CSV should contain the following columns:</p>
            <ul style="text-align: left; display: inline-block; margin: 0 auto;">
                <li><strong>Date:</strong> Transaction date (YYYY-MM-DD or MM/DD/YYYY)</li>
                <li><strong>Amount:</strong> Transaction amount (positive or negative numbers)</li>
                <li><strong>Category:</strong> Expense category (e.g., Food, Transportation, etc.)</li>
            </ul>
            <br>
            <p>📎 <strong>Tip:</strong> You can also include additional columns like Description, Account, etc.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("---")
        st.subheader("✨ Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **� Privacy First**
            - All data stays on your device
            - No cloud uploads
            - Complete data control
            """)
        
        with col2:
            st.markdown("""
            **� Smart Analysis**
            - Automatic data validation
            - Column type detection
            - Data quality checks
            """)
        
        with col3:
            st.markdown("""
            **🎯 Easy to Use**
            - Simple file upload
            - Clear error messages
            - Instant data preview
            """)

if __name__ == "__main__":
    main()
