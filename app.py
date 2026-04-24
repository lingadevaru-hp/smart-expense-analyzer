from flask import Flask, render_template, request, jsonify
import pandas as pd
import io
from datetime import datetime
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
                    'amount': float(row['amount']),
                    'category': row['category'],
                    'reason': f"2x above {category} average"
                })
    
    # Rule 2: Amount > ₹5000 in Food or Entertainment
    for idx, row in df.iterrows():
        if row['category'] in ['Food & Dining', 'Entertainment'] and row['amount'] > 5000:
            anomalies.append({
                'date': row['date'],
                'description': row['description'],
                'amount': float(row['amount']),
                'category': row['category'],
                'reason': f"Exceeds ₹5,000 in {row['category']}"
            })
    
    # Rule 3: Duplicates
    df['date_dt'] = pd.to_datetime(df['date'])
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i < j and row1['description'] == row2['description'] and row1['amount'] == row2['amount']:
                date_diff = abs((row1['date_dt'] - row2['date_dt']).days)
                if date_diff <= 1:
                    anomalies.append({
                        'date': row2['date'],
                        'description': row2['description'],
                        'amount': float(row2['amount']),
                        'category': row2['category'],
                        'reason': f"Duplicate within {date_diff} day(s)"
                    })
    
    # Remove duplicates
    seen = set()
    unique_anomalies = []
    for anom in anomalies:
        key = (anom['date'], anom['amount'], anom['description'])
        if key not in seen:
            seen.add(key)
            unique_anomalies.append(anom)
    
    return unique_anomalies

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle CSV file upload and analysis."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files allowed'}), 400
        
        # Read CSV
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df = pd.read_csv(stream)
        
        # Validate columns
        required_cols = ['date', 'description', 'amount']
        if not all(col in df.columns for col in required_cols):
            return jsonify({'error': f'CSV must contain: {", ".join(required_cols)}'}), 400
        
        # Categorize
        df['category'] = df['description'].apply(categorize_transaction)
        
        # Detect anomalies
        anomalies = detect_anomalies(df)
        
        # Calculate breakdown
        breakdown = df.groupby('category').agg({
            'amount': 'sum',
            'description': 'count'
        }).rename(columns={'description': 'count'}).sort_values('amount', ascending=False)
        
        breakdown_data = []
        for category, row in breakdown.iterrows():
            breakdown_data.append({
                'category': category,
                'total': float(row['amount']),
                'count': int(row['count'])
            })
        
        # Get month
        first_date = pd.to_datetime(df['date'].iloc[0])
        month = first_date.strftime("%B %Y")
        
        total_spent = float(df['amount'].sum())
        avg_transaction = float(df['amount'].mean())
        
        return jsonify({
            'success': True,
            'month': month,
            'total_spent': total_spent,
            'transactions_count': len(df),
            'avg_transaction': avg_transaction,
            'breakdown': breakdown_data,
            'anomalies': anomalies,
            'anomalies_count': len(anomalies)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
