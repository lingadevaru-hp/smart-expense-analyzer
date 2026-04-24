import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Categorization rules
CATEGORY_RULES = {
    "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "food", "pizza", "burger", "dinner", "lunch", "breakfast"],
    "Transportation": ["uber", "ola", "petrol", "diesel", "bus", "auto", "taxi", "ride", "car"],
    "Shopping": ["amazon", "flipkart", "shop", "store", "mall", "ebay"],
    "Entertainment": ["netflix", "spotify", "movie", "game", "theater", "cinema", "concert", "ticket"],
    "Utilities & Bills": ["electricity", "water", "internet", "recharge", "mobile", "wifi", "utility", "bill", "phone"],
    "Healthcare": ["hospital", "pharmacy", "doctor", "medicine", "medical", "clinic", "dentist", "health"],
    "Rent & Housing": ["rent", "pg", "housing", "landlord", "property", "apartment"],
    "Education": ["course", "book", "college", "university", "fee", "tuition", "school", "training"],
}

def categorize_transaction(description):
    """Categorize transaction using keyword matching."""
    desc_lower = description.lower()
    
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category
    
    return "Miscellaneous"

def detect_anomalies(df):
    """Detect anomalies using multiple rules."""
    anomalies = []
    
    # Rule 1: 2x above category average
    for category in df['category'].unique():
        category_df = df[df['category'] == category]
        avg_amount = category_df['amount'].mean()
        
        for idx, row in category_df.iterrows():
            if row['amount'] >= 2 * avg_amount:
                anomalies.append({
                    'date': row['date'],
                    'description': row['description'],
                    'amount': row['amount'],
                    'reason': f"Amount ₹{row['amount']:.0f} is 2x above {category} average (₹{avg_amount:.0f})"
                })
    
    # Rule 2: Amount > ₹5000 in Food or Entertainment
    for idx, row in df.iterrows():
        if row['category'] in ['Food & Dining', 'Entertainment'] and row['amount'] > 5000:
            anomalies.append({
                'date': row['date'],
                'description': row['description'],
                'amount': row['amount'],
                'reason': f"Amount ₹{row['amount']:.0f} exceeds ₹5,000 in {row['category']}"
            })
    
    # Rule 3: Duplicates (same amount + description within 24 hours)
    df['date_dt'] = pd.to_datetime(df['date'])
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i < j and row1['description'] == row2['description'] and row1['amount'] == row2['amount']:
                date_diff = abs((row1['date_dt'] - row2['date_dt']).days)
                if date_diff <= 1:
                    anomalies.append({
                        'date': row2['date'],
                        'description': row2['description'],
                        'amount': row2['amount'],
                        'reason': f"Duplicate: same amount (₹{row2['amount']:.0f}) and description within {date_diff} day(s)"
                    })
    
    # Remove duplicates from anomalies list
    seen = set()
    unique_anomalies = []
    for anom in anomalies:
        key = (anom['date'], anom['amount'], anom['description'])
        if key not in seen:
            seen.add(key)
            unique_anomalies.append(anom)
    
    return unique_anomalies

def generate_report(df, anomalies, month):
    """Generate formatted monthly report."""
    total_spent = df['amount'].sum()
    
    # Breakdown by category
    breakdown = df.groupby('category').agg({
        'amount': 'sum',
        'description': 'count'
    }).rename(columns={'description': 'count'}).sort_values('amount', ascending=False)
    
    # Insights
    highest_category = breakdown.index[0] if len(breakdown) > 0 else "N/A"
    anomaly_categories = [a['reason'].split()[-1] for a in anomalies]
    
    # Generate report text
    report = []
    report.append("=" * 80)
    report.append(f"📊 MONTHLY EXPENSE REPORT — {month}")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"Total Spent: ₹{total_spent:,.0f}")
    report.append("")
    
    report.append("BREAKDOWN BY CATEGORY:")
    report.append("-" * 80)
    report.append(f"{'Category':<25} {'Total Spent':>15} {'No. of Trans':>15}")
    report.append("-" * 80)
    
    for category, row in breakdown.iterrows():
        report.append(f"{category:<25} ₹{row['amount']:>13,.0f} {int(row['count']):>15}")
    
    report.append("-" * 80)
    report.append("")
    
    # Anomalies
    report.append(f"⚠️  ANOMALIES DETECTED: {len(anomalies)}")
    report.append("-" * 80)
    
    if anomalies:
        report.append(f"{'#':<4} {'Date':<12} {'Description':<20} {'Amount':>12} {'Reason':<30}")
        report.append("-" * 80)
        
        for idx, anom in enumerate(anomalies, 1):
            report.append(
                f"{idx:<4} {anom['date']:<12} {anom['description'][:20]:<20} "
                f"₹{anom['amount']:>10,.0f} {anom['reason'][:30]}"
            )
    else:
        report.append("✅ No anomalies detected!")
    
    report.append("")
    report.append("=" * 80)
    report.append("💡 INSIGHTS:")
    report.append("=" * 80)
    report.append(f"• Highest spending category: {highest_category} (₹{breakdown.loc[highest_category, 'amount']:,.0f})")
    report.append(f"• Total transactions: {len(df)}")
    report.append(f"• Anomalies flagged: {len(anomalies)}")
    report.append(f"• Average transaction: ₹{df['amount'].mean():,.0f}")
    report.append("")
    
    if len(anomalies) > 0:
        report.append("⚡ Action Items:")
        report.append(f"  - Review {len(anomalies)} flagged transactions")
        report.append(f"  - {highest_category} is your top spending category")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def analyze_expenses(csv_file, month=None, output_file=None):
    """Main function to analyze expenses."""
    
    # Read CSV
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ Error: File '{csv_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        sys.exit(1)
    
    # Validate required columns
    required_cols = ['date', 'description', 'amount']
    if not all(col in df.columns for col in required_cols):
        print(f"❌ Error: CSV must contain columns: {', '.join(required_cols)}")
        sys.exit(1)
    
    # Categorize
    df['category'] = df['description'].apply(categorize_transaction)
    
    # Detect anomalies
    anomalies = detect_anomalies(df)
    
    # Get month from data if not provided
    if not month:
        try:
            first_date = pd.to_datetime(df['date'].iloc[0])
            month = first_date.strftime("%B %Y")
        except:
            month = "Unknown Month"
    
    # Generate report
    report = generate_report(df, anomalies, month)
    
    # Print to terminal
    print(report)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\n✅ Report saved to: {output_file}")
    
    return df, anomalies

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        month = sys.argv[3] if len(sys.argv) > 3 else None
        analyze_expenses(csv_file, month, output_file)
    else:
        print("Usage: python expense_analyzer.py <csv_file> [output_file] [month]")
        print("\nExample:")
        print("  python expense_analyzer.py transactions.csv report.md 'March 2025'")
