# FinAccess – AI-Powered Credit Risk Assessment Platform

A student-level academic project that demonstrates end-to-end machine learning integration with a Flask web application. It provides instant loan eligibility predictions powered by a Random Forest classifier and explains decisions using SHAP (SHapley Additive exPlanations).

---

## Features

- **Register & Login** with JWT cookie-based authentication
- **Loan Application Form** with 8 financial input features
- **AI Prediction** using a trained RandomForestClassifier
- **SHAP Explanations** – Top 3 positive and negative factors in plain English
- **Application History** – Track all previous submissions
- **Admin Dashboard** – User and application statistics
- **Auto-Setup** – Automatically generates dataset and trains model on first run

---

## Tech Stack

| Layer        | Technology |
|---|---|
| Backend      | Python Flask, Flask-SQLAlchemy, Flask-JWT-Extended |
| Database     | MySQL (Configured via .env) |
| ML           | Scikit-Learn (RandomForestClassifier) |
| Explainability | SHAP (TreeExplainer) |
| Frontend     | HTML5, CSS3, Vanilla JavaScript, Jinja2 |

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

The application connects to a MySQL database using a `DATABASE_URL` environment variable.

Create a `.env` file in the root directory and add your connection string:

```env
DATABASE_URL=mysql+pymysql://username:password@host:port/database_name
```

### 3. Run the Application

```bash
python run.py
```

On **first run**, the app will automatically:
1. Generate 10,000 synthetic loan records → `dataset/loan_data.csv`
2. Train the Random Forest model → `ml/model.pkl`
3. Create database tables
4. Create a default admin account

### 4. Open in Browser

```
http://127.0.0.1:5000
```

---

## Default Admin Credentials

| Field | Value |
|---|---|
| Email | admin@finaccess.com |
| Password | admin123 |

---

## Project Structure

```
FinAccess/
│
├── app/
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── routes/
│   │   ├── auth.py           # Register, Login, Logout
│   │   ├── main.py           # Dashboard, Apply, Result, History
│   │   └── admin.py          # Admin dashboard
│   └── __init__.py           # Flask app factory
│
├── ml/
│   ├── generate_dataset.py   # Synthetic dataset generator
│   ├── train_model.py        # Model training script
│   ├── predict.py            # Prediction + SHAP explanation
│   └── model.pkl             # Trained model (auto-generated)
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   ├── apply.html
│   ├── result.html
│   ├── history.html
│   ├── admin.html
│   └── auth/
│       ├── login.html
│       └── register.html
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
├── dataset/
│   └── loan_data.csv         # Auto-generated on first run
│
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## ML Model Details

- **Algorithm:** RandomForestClassifier (150 estimators, max depth 12)
- **Features:** age, annual_income, employment_type, years_employed, credit_score, existing_debt, loan_amount, loan_term
- **Target:** approval_status (0 = Rejected, 1 = Approved)
- **Train/Test Split:** 80/20
- **Explainability:** SHAP TreeExplainer – top 3 positive and negative factor extraction

### Dataset Generation Rules

| Condition | Effect |
|---|---|
| Income ≥ $80K | Strong approval boost |
| Credit Score ≥ 750 | Highest approval weight |
| Debt/Income > 50% | Strong rejection signal |
| Employment: Unemployed | Significant rejection signal |
| Years Employed < 2 | Increased rejection chance |

---

## Retrain the Model

To retrain from scratch:

```bash
# Delete existing model
del ml\model.pkl

# Optionally delete dataset too
del dataset\loan_data.csv

# Restart the app or run manually
python ml/train_model.py
```
