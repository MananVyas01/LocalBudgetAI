import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime
import io

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
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .upload-section {
        border: 2px dashed #cbd5e1;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 LocalBudgetAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Privacy-First Budget & Expense Analyzer</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Controls")
        st.markdown("---")
        
        # File upload section
        st.subheader("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your transaction data in CSV format"
        )
        
        if uploaded_file is not None:
            st.success("✅ File uploaded successfully!")
            
        st.markdown("---")
        st.subheader("📊 View Options")
        show_raw_data = st.checkbox("Show Raw Data", value=True)
        show_summary = st.checkbox("Show Summary Statistics", value=True)
        show_charts = st.checkbox("Show Visualizations", value=True)
    
    # Main content area
    if uploaded_file is not None:
        try:
            # Load and display data
            df = pd.read_csv(uploaded_file)
            
            # Display success message
            st.success(f"📈 Successfully loaded {len(df)} records from {uploaded_file.name}")
            
            # Create columns for layout
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                if any(col.lower() in ['amount', 'value', 'price', 'total'] for col in df.columns):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        total_amount = df[numeric_cols[0]].sum()
                        st.metric("Total Amount", f"${total_amount:,.2f}")
                    else:
                        st.metric("Total Amount", "N/A")
                else:
                    st.metric("Total Amount", "N/A")
            with col4:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            st.markdown("---")
            
            # Show raw data
            if show_raw_data:
                st.subheader("📋 Raw Data")
                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400
                )
                
                # Download processed data
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="💾 Download Processed Data",
                    data=csv_buffer.getvalue(),
                    file_name=f"processed_{uploaded_file.name}",
                    mime="text/csv"
                )
            
            # Show summary statistics
            if show_summary:
                st.subheader("📊 Summary Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Data Types:**")
                    dtype_df = pd.DataFrame({
                        'Column': df.dtypes.index,
                        'Data Type': df.dtypes.values
                    })
                    st.dataframe(dtype_df, use_container_width=True)
                
                with col2:
                    st.write("**Missing Values:**")
                    missing_df = pd.DataFrame({
                        'Column': df.columns,
                        'Missing Count': df.isnull().sum().values,
                        'Missing %': (df.isnull().sum() / len(df) * 100).round(2).values
                    })
                    st.dataframe(missing_df, use_container_width=True)
                
                # Numeric summary
                numeric_columns = df.select_dtypes(include=['number']).columns
                if len(numeric_columns) > 0:
                    st.write("**Numeric Summary:**")
                    st.dataframe(df[numeric_columns].describe(), use_container_width=True)
            
            # Show visualizations
            if show_charts and len(df) > 0:
                st.subheader("📈 Data Visualizations")
                
                # Create tabs for different chart types
                tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Trends", "🔍 Distribution"])
                
                with tab1:
                    # Basic data overview charts
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Bar chart of numeric columns
                            st.write("**Numeric Columns Summary**")
                            fig, ax = plt.subplots(figsize=(10, 6))
                            numeric_summary = df[numeric_cols].sum()
                            ax.bar(numeric_summary.index, numeric_summary.values)
                            ax.set_title("Sum of Numeric Columns")
                            plt.xticks(rotation=45)
                            st.pyplot(fig)
                        
                        with col2:
                            # Data completeness
                            st.write("**Data Completeness**")
                            completeness = (1 - df.isnull().sum() / len(df)) * 100
                            fig, ax = plt.subplots(figsize=(10, 6))
                            ax.bar(completeness.index, completeness.values)
                            ax.set_title("Data Completeness by Column (%)")
                            ax.set_ylabel("Completeness %")
                            plt.xticks(rotation=45)
                            st.pyplot(fig)
                
                with tab2:
                    st.write("**Trend Analysis**")
                    # Look for date columns
                    date_cols = []
                    for col in df.columns:
                        if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                            date_cols.append(col)
                    
                    if date_cols and len(numeric_cols) > 0:
                        selected_date_col = st.selectbox("Select Date Column:", date_cols)
                        selected_numeric_col = st.selectbox("Select Numeric Column:", numeric_cols)
                        
                        try:
                            # Convert to datetime
                            df_temp = df.copy()
                            df_temp[selected_date_col] = pd.to_datetime(df_temp[selected_date_col])
                            df_temp = df_temp.sort_values(selected_date_col)
                            
                            # Plot trend
                            fig = px.line(
                                df_temp, 
                                x=selected_date_col, 
                                y=selected_numeric_col,
                                title=f"{selected_numeric_col} over Time"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        except:
                            st.warning("Could not create trend chart. Please check your date format.")
                    else:
                        st.info("No suitable date or numeric columns found for trend analysis.")
                
                with tab3:
                    st.write("**Distribution Analysis**")
                    if len(numeric_cols) > 0:
                        selected_col = st.selectbox("Select Column for Distribution:", numeric_cols)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Histogram
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.hist(df[selected_col].dropna(), bins=30, alpha=0.7)
                            ax.set_title(f"Distribution of {selected_col}")
                            ax.set_xlabel(selected_col)
                            ax.set_ylabel("Frequency")
                            st.pyplot(fig)
                        
                        with col2:
                            # Box plot
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.boxplot(df[selected_col].dropna())
                            ax.set_title(f"Box Plot of {selected_col}")
                            ax.set_ylabel(selected_col)
                            st.pyplot(fig)
                    else:
                        st.info("No numeric columns found for distribution analysis.")
            
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            st.info("Please make sure your file is a valid CSV format.")
    
    else:
        # Welcome screen
        st.markdown("""
        <div class="upload-section">
            <h2>🚀 Get Started</h2>
            <p>Upload your CSV file using the sidebar to begin analyzing your budget data!</p>
            <br>
            <h3>📋 Expected Data Format</h3>
            <p>Your CSV should ideally contain columns such as:</p>
            <ul style="text-align: left; display: inline-block;">
                <li><strong>Date:</strong> Transaction date</li>
                <li><strong>Description:</strong> Transaction description</li>
                <li><strong>Amount:</strong> Transaction amount</li>
                <li><strong>Category:</strong> Expense category (optional)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature showcase
        st.markdown("---")
        st.subheader("✨ Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Data Analysis**
            - Automatic data type detection
            - Missing value analysis
            - Summary statistics
            - Data quality checks
            """)
        
        with col2:
            st.markdown("""
            **📈 Visualizations**
            - Interactive charts
            - Trend analysis
            - Distribution plots
            - Customizable views
            """)
        
        with col3:
            st.markdown("""
            **🔒 Privacy First**
            - All data stays local
            - No cloud uploads
            - Secure processing
            - Your data, your control
            """)

if __name__ == "__main__":
    main()
