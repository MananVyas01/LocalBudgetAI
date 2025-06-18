# 💰 LocalBudgetAI

<div align="center">

**Your Privacy-First Budget & Expense Analyzer**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)
![Status](https://img.shields.io/badge/status-production%20ready-green.svg)

*Transform your financial data into actionable insights with professional visualizations and AI-powered analysis—all while keeping your data completely private and local.*

</div>

---

## ✨ Features

### 🎯 **Core Analytics**
- 📊 **Interactive Visualizations** - Beautiful Plotly charts with hover details, zoom, and export capabilities
- 💰 **Budget Tracking** - Comprehensive income, expense, and savings analysis
- � **Trend Analysis** - Monthly patterns, category breakdowns, and comparative insights
- 🔍 **Advanced Filtering** - Date ranges, categories, amounts with session persistence

### 🤖 **AI-Powered Assistant**
- **Dual LLM Support** - Choose between Mistral and Llama3 models via Ollama
- **Natural Language Queries** - Ask questions about your spending in plain English
- **Context-Aware Responses** - AI analyzes your filtered data for personalized insights
- **Automatic Fallback** - Seamless switching between models if one fails

### 🎨 **Professional UI/UX**
- **Modern Interface** - Clean, responsive design that works on all devices
- **Session State Memory** - Remembers your preferences and filter settings
- **Quick Actions** - Streamlined workflows for common tasks
- **Real-time Updates** - Dynamic charts and statistics that update instantly

### 🔒 **Privacy & Security**
- **100% Local** - All data stays on your machine, never sent to external servers
- **Offline-First** - Works completely offline (AI features optional)
- **No Cloud Dependencies** - Your financial data remains under your control
- **SQLite Database** - Reliable local storage with data integrity

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** 
- **pip** (Python package manager)
- **Ollama** (optional, for AI features) - [Install Ollama](https://ollama.ai/download)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MananVyas01/LocalBudgetAI.git
cd LocalBudgetAI
```

2. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Launch the application:**
```bash
streamlit run app/main.py
```

5. **Open your browser:** Navigate to `http://localhost:8501`

### Optional: AI Assistant Setup

For AI-powered insights, install Ollama and download models:

```bash
# Install required models
ollama pull mistral
ollama pull llama3

# Verify installation
ollama list
```

---

## 📋 Usage Guide

### 1. **Data Input**
- **Manual Entry**: Add individual transactions through the intuitive form
- **CSV Upload**: Bulk import your bank statements or expense exports
- **Supported Formats**: Date, Amount, Category, Description columns

### 2. **Dashboard Analytics**
- **Overview Tab**: High-level metrics and key insights
- **Trends Tab**: Monthly analysis with growth rates and patterns
- **Details Tab**: Category breakdowns and detailed statistics  
- **Compare Tab**: Side-by-side category comparisons over time

### 3. **Advanced Filtering**
- **Date Ranges**: Analyze specific time periods
- **Category Selection**: Focus on particular expense types
- **Amount Filtering**: Filter by transaction size
- **Quick Filters**: "This Month", "Last 30 Days" shortcuts

### 4. **AI Assistant**
- **Model Selection**: Choose between Mistral or Llama3
- **Natural Queries**: "What did I spend most on this month?"
- **Context-Aware**: Analyzes your current filtered data
- **Smart Suggestions**: Example questions to get started

---

## 🗂️ Project Structure

```
LocalBudgetAI/
├── 📄 README.md              # Project documentation
├── 📄 requirements.txt       # Python dependencies
├── 📁 app/                   # Application source code
│   ├── 🐍 main.py           # Main Streamlit application
│   ├── 🐍 database.py       # SQLite database operations
│   ├── 🐍 analyzer.py       # Core analysis functions
│   ├── 🐍 plotly_analyzer.py # Interactive visualizations
│   └── 🐍 llm_helper.py     # AI assistant integration
├── 📁 data/                  # Data storage directory
└── 📁 tests/                 # Test files
    ├── 🧪 test_stage5.py     # UI/UX functionality tests
    └── 🧪 test_stage6.py     # AI features tests
```

---

## 📊 Expected Data Format

Your CSV files should contain these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **Date** | Date | Transaction date | `2024-01-15` or `01/15/2024` |
| **Amount** | Number | Transaction amount (+ income, - expense) | `-45.67` or `2500.00` |
| **Category** | Text | Expense category | `Groceries`, `Entertainment` |
| **Description** | Text | Transaction details | `Whole Foods Market` |

### Sample CSV:
```csv
Date,Amount,Category,Description
2024-01-15,-45.67,Groceries,Whole Foods Market
2024-01-16,-12.50,Transportation,Metro Card
2024-01-20,2500.00,Income,Salary Deposit
```

---

## 🎨 Screenshots

### Dashboard Overview
The main dashboard provides comprehensive insights with interactive charts:

- **Category Breakdown**: Visual spending distribution
- **Monthly Trends**: Track spending patterns over time  
- **Quick Stats**: Key metrics at a glance
- **Filter Controls**: Powerful data exploration tools

### AI Assistant
Natural language queries make data analysis intuitive:

- **Contextual Analysis**: AI understands your current filters
- **Example Questions**: Get started with suggested queries
- **Model Selection**: Choose between Mistral and Llama3
- **Conversation History**: Review past insights

---

## 🛠️ Development

### Running Tests
```bash
# Test Stage 5 features (UI/UX)
python test_stage5.py

# Test Stage 6 features (AI Assistant)  
python test_stage6.py
```

### Contributing Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 conventions
- Add docstrings to all functions
- Include type hints where applicable
- Write tests for new features

---

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set default Ollama model
export PREFERRED_LLM_MODEL=mistral

# Optional: Custom database location
export BUDGET_DB_PATH=/path/to/custom/location
```

### Advanced Configuration
Edit `app/main.py` to customize:
- Chart color schemes
- Default filter settings
- UI layout preferences
- Database configuration

---

## 📈 Roadmap

### Upcoming Features
- [ ] **Budget Goals & Alerts** - Set spending limits and receive notifications
- [ ] **Export Capabilities** - PDF reports and data exports
- [ ] **Multi-Currency Support** - International currency handling
- [ ] **Mobile App** - Native mobile application
- [ ] **Advanced ML Models** - Spending prediction and anomaly detection

### Recently Completed
- ✅ **Stage 5**: Enhanced UI/UX with Plotly visualizations
- ✅ **Stage 6**: Dual LLM model support with Ollama integration
- ✅ **Advanced Filtering**: Session-persistent filter system
- ✅ **Professional Dashboard**: Multi-tab analytics interface

---

## 🆘 Troubleshooting

### Common Issues

**Q: Charts not displaying properly**
```bash
# Update Plotly to latest version
pip install --upgrade plotly
```

**Q: AI Assistant not working**
```bash
# Check Ollama installation
ollama --version

# Verify models are installed
ollama list

# Pull required models if missing
ollama pull mistral
ollama pull llama3
```

**Q: CSV upload fails**
- Ensure your CSV has the required columns (Date, Amount)
- Check for proper date formatting (YYYY-MM-DD or MM/DD/YYYY)
- Verify numeric amounts don't contain currency symbols

**Q: Database errors**
```bash
# Reset database (WARNING: This deletes all data)
rm data/expenses.db

# Restart the application
streamlit run app/main.py
```

---

## 📞 Support & Community

- **Issues**: Report bugs on [GitHub Issues](https://github.com/MananVyas01/LocalBudgetAI/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/MananVyas01/LocalBudgetAI/discussions)
- **Documentation**: Visit our [Wiki](https://github.com/MananVyas01/LocalBudgetAI/wiki)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Streamlit** - For the excellent web framework
- **Plotly** - For beautiful interactive visualizations  
- **Ollama** - For local LLM capabilities
- **pandas** - For powerful data manipulation
- **SQLite** - For reliable local data storage

---

<div align="center">

**Built with ❤️ for privacy-conscious financial management**

*Star ⭐ this repo if you find it useful!*

</div>
