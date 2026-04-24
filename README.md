# Smart Expense Analyzer

A simple, production-ready Python script that analyzes financial transactions, categorizes expenses, detects anomalies, and generates monthly reports.

## What It Does

✅ **Reads CSV files** with transaction data  
✅ **Categorizes transactions** using keyword matching (8 categories)  
✅ **Detects anomalies** using 3 rules:
  - Amount 2x above category average
  - Duplicates (same amount + description within 24hrs)
  - Amount > ₹5000 in Food or Entertainment

✅ **Generates clean reports** — prints to terminal + saves as markdown  
✅ **Zero dependencies** — uses only pandas & standard library  

## Quick Start

### Setup (One time)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pandas
```

### Usage
```bash
python3 expense_analyzer.py <csv_file> [output_file] [month]
```

### Examples
```bash
# Analyze and print to terminal
python3 expense_analyzer.py transactions.csv

# Analyze, save report, and specify month
python3 expense_analyzer.py transactions.csv report.md "March 2025"

# Just print, no file
python3 expense_analyzer.py transactions.csv "" "March 2025"
```

## CSV Format

Your input file must have 3 columns:
```csv
date,description,amount
2025-03-01,Swiggy Dinner,450
2025-03-02,Uber to airport,1200
2025-03-05,Amazon order,3400
```

## Categories

The script automatically categorizes transactions into:
- **Food & Dining** — Swiggy, Zomato, restaurant, cafe, food
- **Transportation** — Uber, Ola, petrol, bus, auto, taxi
- **Shopping** — Amazon, Flipkart, shop, store, mall
- **Entertainment** — Netflix, Spotify, movie, game, concert
- **Utilities & Bills** — electricity, water, internet, recharge, mobile
- **Healthcare** — hospital, pharmacy, doctor, medicine
- **Rent & Housing** — rent, PG, housing, property
- **Education** — course, book, college, university, fee
- **Miscellaneous** — anything else

## Anomaly Detection Rules

1. **2x Category Average**  
   Flags any transaction 2x above its category's average spending

2. **Duplicates**  
   Flags identical amounts + descriptions within 24 hours (potential double charges)

3. **Amount Thresholds**  
   Flags Food & Entertainment expenses > ₹5000

## Report Output

The generated report includes:
- Total spending
- Breakdown by category (with counts)
- Flagged anomalies with reasons
- Insights & action items

Example output saved to `report.md`:
```
📊 MONTHLY EXPENSE REPORT — March 2025
================================================

Total Spent: ₹30,479

BREAKDOWN BY CATEGORY:
Shopping              ₹10,200   (3 transactions)
Rent & Housing       ₹8,000    (1 transaction)
Food & Dining        ₹7,230    (3 transactions)
...

⚠️  ANOMALIES DETECTED: 2
1. Swiggy Dinner (₹6,500) — exceeds ₹5,000 threshold
2. Amazon order (₹3,400) — duplicate within 24 hours
...
```

## Customization

### Add/Modify Categories
Edit `CATEGORY_RULES` in `expense_analyzer.py`:
```python
CATEGORY_RULES = {
    "Food & Dining": ["swiggy", "zomato", ...],
    "Your Category": ["keyword1", "keyword2", ...],
}
```

### Change Anomaly Thresholds
Modify the detection rules in `detect_anomalies()`:
- Line ~48: Change `2 * avg_amount` to desired multiplier
- Line ~59: Change `5000` to different amount threshold
- Line ~68: Change `<= 1` for different time window

## Example Workflow

```bash
# 1. Prepare your CSV
cat transactions.csv

# 2. Run analysis
python3 expense_analyzer.py transactions.csv report.md "March 2025"

# 3. View report in terminal (already printed)
# 4. Review saved markdown file
cat report.md
```

## Requirements

- Python 3.7+
- pandas
- CSV file with date, description, amount columns

That's it. No databases, no frameworks, no complexity.

## License

MIT — Use freely for academic projects
