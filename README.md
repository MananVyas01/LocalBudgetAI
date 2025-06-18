# LocalBudgetAI

A local, offline-first budget & expense analyzer that provides clean visualizations, spending insights, and optional Ollama-powered LLM chat for natural language queries. Built with privacy-first design, ideal for personal finance tracking.

## Features

- 📊 **Data Visualization**: Interactive charts and graphs for expense analysis
- 💰 **Budget Tracking**: Track income, expenses, and savings goals
- 🔒 **Privacy-First**: All data stays local on your machine
- 📱 **Web Interface**: Clean, modern Streamlit-based UI
- 🤖 **AI Chat**: Optional Ollama integration for natural language queries
- 📈 **Insights**: Automated spending pattern analysis

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MananVyas01/LocalBudgetAI.git
cd LocalBudgetAI
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app/main.py
```

5. Open your browser to `http://localhost:8501`

## Project Structure

```
LocalBudgetAI/
├── README.md
├── requirements.txt
├── .gitignore
├── app/
│   └── main.py
└── data/
    └── .gitkeep
```

## Usage

1. Upload your CSV file containing transaction data
2. View your data in the interactive dashboard
3. Analyze spending patterns with built-in visualizations
4. Use the AI chat feature for natural language queries (optional)

## Data Format

Your CSV should contain columns like:
- Date
- Description
- Amount
- Category (optional)

## Contributing

This project is designed for personal use but contributions are welcome!

## License

MIT License
