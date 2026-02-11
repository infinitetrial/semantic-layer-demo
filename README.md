# Semantic Layer Demo

A demonstration of how semantic layers solve the "different definitions" problem in data analytics, powered by AI.

## 🎯 Problem Statement

Without a semantic layer, different teams define metrics differently:
- **Marketing**: "High value customer" = anyone who spent >$1000
- **Finance**: "High value customer" = top 20% by revenue
- **Sales**: "High value customer" = recent buyers with >$500 spend

**Result:** The same question yields three conflicting answers depending on who you ask.

## ✅ Solution: Semantic Layer

A semantic layer provides:
1. **Taxonomy** - Standardized customer segments and categories
2. **Metadata** - Column-level documentation and business context
3. **Metrics** - Certified calculations with clear ownership

**Result:** One source of truth, consistent answers.

## 📊 Dataset

**Source:** [Customer Personality Analysis](https://www.kaggle.com/datasets/imakash3011/customer-personality-analysis) on Kaggle

- 2,240 customer records
- 29 features including demographics, spending patterns, and campaign responses
- 2-year observation period
- Used to demonstrate semantic layer concepts with realistic business data

## 🏗️ Architecture
```
User Question → Google AI (Gemini) → Semantic Layer → SQL → DuckDB → Results
```

### Components:
- **Backend**: Python (FastAPI coming soon)
  - `semantic_parser.py` - Reads YAML definitions
  - `query_generator.py` - Generates SQL from semantic layer
  - `llm_client.py` - Natural language understanding via Gemini
- **Data Layer**: DuckDB with customer analytics dataset
- **Semantic Layer**: YAML files defining taxonomy, metadata, and metrics
- **Frontend**: (Coming soon - React/Next.js)

## 📊 Demo Queries
```
"What's average spending for parents?"
→ Uses taxonomy: family_status.parents (Kidhome > 0 OR Teenhome > 0)
→ Uses metric: total_spending (sum of all product categories)
→ Result: $613.45

"Compare CLV for high value vs low value customers"
→ Uses taxonomy: value_tiers.high_value, value_tiers.low_value
→ Uses metric: customer_lifetime_value (annual spending)
→ Result: Shows comparison table
```

## 🚀 Tech Stack

- **Python 3.14** - Backend logic
- **FastAPI** - REST API (coming soon)
- **DuckDB** - Analytics database
- **Google AI (Gemini 2.5)** - Natural language understanding
- **YAML** - Semantic layer definitions
- **Next.js** (planned) - Frontend UI
- **Vercel/Railway** (planned) - Deployment

## 📁 Project Structure
```
semantic-layer-demo/
├── backend/
│   ├── semantic_parser.py      # Reads YAML semantic layer
│   ├── query_generator.py      # Converts intent → SQL
│   └── llm_client.py            # Google AI integration
├── semantic/
│   ├── taxonomy.yml             # Customer segments & categories
│   ├── metadata.yml             # Column documentation
│   └── semantic_layer.yml       # Metric definitions
├── data/
│   └── marketing_campaign.csv   # Customer dataset (2,240 records)
└── README.md
```

## 🎓 Key Concepts Demonstrated

### 1. Taxonomy
- Customer age segments (dynamic calculation)
- Family status (parents vs no children)
- Value tiers (high/medium/low value)
- Product categories (beverages, food, luxury)

### 2. Metadata
- Column-level descriptions
- Business ownership
- PII classification
- Data quality 

**Note:** Business owners (Marketing Team, Product Team, etc.) are illustrative examples for demonstration purposes. In production, these would be actual team names and individuals.

### 3. Semantic Layer
- Metric definitions (CLV, engagement score, churn risk)
- Consistent calculations
- Clear ownership
- Business context

## 🔧 Local Development

### Prerequisites
```bash
Python 3.14+
pip install pyyaml duckdb google-generativeai pandas
```

### Setup
```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/semantic-layer-demo.git
cd semantic-layer-demo

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set Google AI API key
set GOOGLE_API_KEY=your-key-here  # Windows (Command Prompt)
$env:GOOGLE_API_KEY="your-key-here"  # Windows (PowerShell)
export GOOGLE_API_KEY=your-key-here  # Mac/Linux
```

### Run Tests
```bash
# Test semantic parser
python backend/semantic_parser.py

# Test query generator
python backend/query_generator.py

# Test full pipeline with AI
python backend/llm_client.py
```

## 📈 Results

The semantic layer ensures:
- ✅ **Consistency** - Same question always yields same SQL
- ✅ **Governance** - Clear metric ownership and approval process
- ✅ **Transparency** - Business logic is documented and auditable
- ✅ **Efficiency** - AI can query data using standardized definitions

## 🚧 Roadmap

- [ ] FastAPI wrapper for HTTP endpoints
- [ ] React/Next.js frontend with split-screen demo
- [ ] Deploy to Vercel
- [ ] Add more complex metrics (cohort analysis, retention)
- [ ] Support for multiple datasets

## 📝 License

MIT

## 🤝 Contributing

This is a demonstration project. Feel free to fork and adapt for your own use cases!

## 📧 Contact

Questions? Connect with me on https://www.linkedin.com/in/ciaralwhite/

---

**Built to demonstrate the importance of semantic layers in modern data architecture.**
```

---

## Step 5: Create requirements.txt

**Create `requirements.txt` in project root:**
```
pyyaml==6.0.3
duckdb==1.4.4
google-generativeai==0.8.6
pandas==3.0.0
requests==2.32.5