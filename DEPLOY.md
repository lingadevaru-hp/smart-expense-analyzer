# Web UI - Easy Deployment Guide

## What You Now Have

✅ **Complete web app** with:
- Modern, beautiful UI (drag & drop, charts, responsive)
- Flask backend
- Zero frontend build complexity (HTML/CSS/JS in one file)
- Charts using Chart.js
- Works on any browser

---

## Run Locally

```bash
# 1. Install dependencies
pip install -r requirements-web.txt

# 2. Start server
python3 app.py

# 3. Open browser
http://localhost:5000
```

---

## Deploy Easily (Pick One)

### **Option 1: Render.com (Free, Recommended)**

1. **Sign up** at https://render.com
2. **Create file** `render.yaml` in project root:
```yaml
services:
  - type: web
    name: expense-analyzer
    env: python
    plan: free
    buildCommand: pip install -r requirements-web.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

3. **Push to GitHub** (if not already):
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/expense-analyzer.git
git push -u origin main
```

4. **Connect on Render:**
   - Go to Dashboard → New → Web Service
   - Connect GitHub repo
   - It auto-detects and deploys!

**Your app will be live at:** `https://your-app.onrender.com`

---

### **Option 2: PythonAnywhere.com (Free)**

1. Sign up at https://pythonanywhere.com
2. Upload files via web interface
3. Create a "Web app" with Flask
4. Point to `app.py`
5. Done!

**Your app will be live at:** `https://yourusername.pythonanywhere.com`

---

### **Option 3: Heroku (Paid, $7/month)**

1. **Create `Procfile`:**
```
web: python app.py
```

2. **Login and deploy:**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

### **Option 4: Your Own Server (VPS)**

**On Ubuntu/Debian VPS:**

```bash
# 1. Install Python
sudo apt update
sudo apt install python3-pip python3-venv

# 2. Clone your code
git clone https://github.com/your-repo expense-analyzer
cd expense-analyzer

# 3. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-web.txt

# 4. Run with Gunicorn
pip install gunicorn
gunicorn app:app

# 5. Setup Nginx reverse proxy (optional)
# ... (guide available on request)
```

---

## File Structure

```
expense-analyzer/
├── app.py                      # Flask backend
├── requirements-web.txt        # Dependencies
├── expense_analyzer.py         # CLI analyzer (for reference)
├── templates/
│   └── index.html             # Web UI (one file!)
└── transactions.csv           # Sample data
```

---

## Features

✅ **Upload CSV** — Drag & drop or click to select  
✅ **Auto-categorize** — 8 categories using keywords  
✅ **Detect anomalies** — 3 detection rules  
✅ **Beautiful charts** — Bar chart, pie chart  
✅ **Responsive** — Works on mobile, tablet, desktop  
✅ **Fast** — No build process, no compilation  
✅ **Secure** — File size limit (16MB)  

---

## CSV Format Required

```csv
date,description,amount
2025-03-01,Swiggy Dinner,450
2025-03-02,Uber to airport,1200
```

Just 3 columns. That's it!

---

## Troubleshooting

**Port 5000 already in use?**
```bash
python3 app.py --port 5001
```

**ModuleNotFoundError: No module named 'flask'**
```bash
pip install flask pandas
```

**Upload fails**
- Check file is CSV
- Check file size < 16MB
- Check columns: date, description, amount

---

## Next Steps

1. **Test locally** first:
```bash
python3 app.py
# Then open http://localhost:5000
```

2. **Deploy to Render/PythonAnywhere** (5 minutes)

3. **Share your link** with friends/professors!

---

## Need More Features?

Easy to add:
- Budget tracking per category
- Multiple CSV uploads
- Data export (PDF reports)
- User accounts
- Database persistence

Just ask! 🚀
