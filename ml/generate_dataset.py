import os
import sys
import random
import numpy as np
import pandas as pd

# Ensure dataset directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'dataset'), exist_ok=True)
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'loan_data.csv')

def generate_dataset(n=10000, seed=42):
    """Generate synthetic loan dataset with realistic approval rules."""
    random.seed(seed)
    np.random.seed(seed)

    records = []

    employment_types = ['Employed', 'Self-Employed', 'Unemployed']

    for _ in range(n):
        age = int(np.random.randint(21, 65))
        annual_income = int(np.random.choice(
            [np.random.randint(15000, 40000),
             np.random.randint(40000, 90000),
             np.random.randint(90000, 250000)],
            p=[0.35, 0.45, 0.20]
        ))
        employment_type = np.random.choice(employment_types, p=[0.60, 0.28, 0.12])
        years_employed = int(np.random.randint(0, 30))
        credit_score = int(np.clip(np.random.normal(650, 100), 300, 850))
        existing_debt = int(np.random.randint(0, min(annual_income, 80000)))
        loan_amount = int(np.random.randint(5000, 300000))
        loan_term = int(np.random.choice([12, 24, 36, 48, 60, 120, 180, 240, 360]))

        # Approval score based on realistic rules
        score = 0.0

        # Income factor
        if annual_income >= 80000:
            score += 2.5
        elif annual_income >= 40000:
            score += 1.5
        elif annual_income >= 20000:
            score += 0.5
        else:
            score -= 1.0

        # Credit score factor
        if credit_score >= 750:
            score += 3.0
        elif credit_score >= 700:
            score += 2.0
        elif credit_score >= 650:
            score += 1.0
        elif credit_score >= 600:
            score -= 0.5
        else:
            score -= 2.5

        # Employment type factor
        if employment_type == 'Employed':
            score += 1.5
        elif employment_type == 'Self-Employed':
            score += 0.5
        else:
            score -= 2.0

        # Years employed factor
        if years_employed >= 5:
            score += 1.5
        elif years_employed >= 2:
            score += 0.5
        elif years_employed >= 1:
            score -= 0.5
        else:
            score -= 1.5

        # Debt-to-income ratio factor
        debt_to_income = existing_debt / max(annual_income, 1)
        if debt_to_income > 0.5:
            score -= 2.5
        elif debt_to_income > 0.35:
            score -= 1.5
        elif debt_to_income > 0.20:
            score -= 0.5
        else:
            score += 0.5

        # Loan amount vs income factor
        loan_ratio = loan_amount / max(annual_income, 1)
        if loan_ratio > 10:
            score -= 2.0
        elif loan_ratio > 5:
            score -= 1.0
        elif loan_ratio > 2:
            score -= 0.25

        # Age factor (very young or very close to retirement = slight risk)
        if age < 25 or age > 60:
            score -= 0.5

        # Convert score to probability and decide
        approval_prob = 1 / (1 + np.exp(-score * 0.5))
        approval_status = 1 if np.random.random() < approval_prob else 0

        records.append({
            'age': age,
            'annual_income': annual_income,
            'employment_type': employment_type,
            'years_employed': years_employed,
            'credit_score': credit_score,
            'existing_debt': existing_debt,
            'loan_amount': loan_amount,
            'loan_term': loan_term,
            'approval_status': approval_status
        })

    df = pd.DataFrame(records)
    df.to_csv(DATASET_PATH, index=False)
    approved = df['approval_status'].sum()
    print(f"[Dataset] Generated {n} records. Approved: {approved} ({approved/n*100:.1f}%), Rejected: {n-approved} ({(n-approved)/n*100:.1f}%)")
    return df


if __name__ == '__main__':
    if os.path.exists(DATASET_PATH):
        print(f"[Dataset] Already exists at: {DATASET_PATH}")
    else:
        generate_dataset()
