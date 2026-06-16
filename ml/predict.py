import os
import sys
import pickle
import numpy as np

ML_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(ML_DIR, 'model.pkl')

EMPLOYMENT_MAP = {'Employed': 2, 'Self-Employed': 1, 'Unemployed': 0}

# Human-readable feature labels for SHAP explanations
FEATURE_LABELS = {
    'age': 'Age',
    'annual_income': 'Annual Income',
    'employment_type': 'Employment Type',
    'years_employed': 'Years of Employment',
    'credit_score': 'Credit Score',
    'existing_debt': 'Existing Debt',
    'loan_amount': 'Loan Amount',
    'loan_term': 'Loan Term'
}

# Positive impact: feature pushed toward approval
POSITIVE_TEMPLATES = {
    'annual_income': 'Strong annual income of ${val:,} supports repayment ability',
    'credit_score': 'Healthy credit score of {val} demonstrates creditworthiness',
    'years_employed': '{val} years of stable employment reduces risk',
    'employment_type': 'Employment status ({label}) adds financial stability',
    'age': 'Applicant age of {val} is within a favorable lending range',
    'existing_debt': 'Low existing debt of ${val:,} keeps your debt profile clean',
    'loan_amount': 'Requested loan amount is proportionate to your profile',
    'loan_term': 'Loan term of {val} months is manageable',
}

# Negative impact: feature pushed toward rejection
NEGATIVE_TEMPLATES = {
    'annual_income': 'Annual income of ${val:,} may limit repayment capacity',
    'credit_score': 'Credit score of {val} indicates elevated credit risk',
    'years_employed': 'Limited employment history of {val} year(s) increases risk',
    'employment_type': 'Employment status ({label}) is considered higher risk',
    'age': 'Applicant age of {val} falls outside the optimal lending range',
    'existing_debt': 'Existing debt of ${val:,} significantly increases risk burden',
    'loan_amount': 'Requested loan amount appears high relative to your profile',
    'loan_term': 'Long loan term of {val} months increases exposure risk',
}

EMPLOYMENT_REVERSE = {2: 'Employed', 1: 'Self-Employed', 0: 'Unemployed'}


def load_model():
    """Load model from disk, training it first if not found."""
    if not os.path.exists(MODEL_PATH):
        print("[Predict] Model not found. Auto-training...")
        sys.path.insert(0, ML_DIR)
        from train_model import train_model
        return train_model()

    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def format_explanation(feature, shap_val, input_data):
    """Create a user-friendly explanation string for a SHAP feature impact."""
    val = input_data.get(feature)
    is_positive = shap_val > 0

    if feature == 'employment_type':
        label = EMPLOYMENT_REVERSE.get(int(val), 'Unknown')
        templates = POSITIVE_TEMPLATES if is_positive else NEGATIVE_TEMPLATES
        return templates[feature].format(val=val, label=label)

    templates = POSITIVE_TEMPLATES if is_positive else NEGATIVE_TEMPLATES
    template = templates.get(feature, f"{FEATURE_LABELS.get(feature, feature)} had an impact")
    try:
        if 'val' in template:
            return template.format(val=val)
        return template
    except Exception:
        return f"{FEATURE_LABELS.get(feature, feature)} influenced the decision"


def predict(input_data: dict) -> dict:
    """
    Run loan approval prediction and SHAP explanation.

    Args:
        input_data: dict with keys matching FEATURE_COLS

    Returns:
        dict with risk_score, approval_probability, decision, explanations
    """
    model_data = load_model()
    model = model_data['model']
    feature_cols = model_data['feature_cols']

    # Encode employment type
    emp_encoded = EMPLOYMENT_MAP.get(input_data.get('employment_type', 'Employed'), 2)

    # Build feature vector
    features = {
        'age': int(input_data['age']),
        'annual_income': float(input_data['annual_income']),
        'employment_type': emp_encoded,
        'years_employed': int(input_data['years_employed']),
        'credit_score': int(input_data['credit_score']),
        'existing_debt': float(input_data['existing_debt']),
        'loan_amount': float(input_data['loan_amount']),
        'loan_term': int(input_data['loan_term']),
    }

    import pandas as pd
    X = pd.DataFrame([features], columns=feature_cols)

    # Predict
    approval_prob = model.predict_proba(X)[0][1]
    decision = 'Approved' if approval_prob >= 0.5 else 'Rejected'

    # Risk score: 100 = safest (fully approved), 0 = riskiest (fully rejected)
    risk_score = int(round(approval_prob * 100))
    approval_probability = int(round(approval_prob * 100))

    # SHAP Explanation
    try:
        import shap
        import numpy as np
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        # SHAP 0.40-0.44: returns list [class0_array, class1_array]
        # SHAP 0.45+: may return 3D array (n_samples, n_features, n_classes)
        # SHAP 0.52+: returns Explanation object or ndarray
        if isinstance(shap_values, list):
            # Old API: list of arrays per class
            sv = np.array(shap_values[1][0])
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3:
                # 3D: (samples, features, classes) — use class 1
                sv = shap_values[0, :, 1]
            elif shap_values.ndim == 2:
                # 2D: (samples, features)
                sv = shap_values[0]
            else:
                sv = shap_values
        else:
            # Explanation object (shap >= 0.45)
            vals = shap_values.values
            if vals.ndim == 3:
                sv = vals[0, :, 1]
            elif vals.ndim == 2:
                sv = vals[0]
            else:
                sv = vals

        sv = np.array(sv, dtype=float).flatten()

        # Map feature names to SHAP values
        shap_map = dict(zip(feature_cols, sv))

        # Sort features by SHAP value
        sorted_features = sorted(shap_map.items(), key=lambda x: float(x[1]), reverse=True)

        # Positive factors (push toward approval)
        positive_factors = [(f, v) for f, v in sorted_features if float(v) > 0][:3]
        # Negative factors (push toward rejection)
        negative_factors = [(f, v) for f, v in reversed(sorted_features) if float(v) < 0][:3]

        # Build raw input dict for templates (with original string employment_type)
        raw_data = dict(features)
        raw_data['employment_type'] = emp_encoded  # already numeric

        positive_text = [format_explanation(f, v, raw_data) for f, v in positive_factors]
        negative_text = [format_explanation(f, v, raw_data) for f, v in negative_factors]

    except Exception as e:
        print(f"[SHAP Warning] Could not compute SHAP values: {e}")
        positive_text = ["Prediction computed successfully"]
        negative_text = []

    return {
        'risk_score': risk_score,
        'approval_probability': approval_probability,
        'decision': decision,
        'explanations': {
            'positive': positive_text,
            'negative': negative_text
        }
    }


if __name__ == '__main__':
    # Quick test
    sample = {
        'age': 35,
        'annual_income': 95000,
        'employment_type': 'Employed',
        'years_employed': 8,
        'credit_score': 740,
        'existing_debt': 12000,
        'loan_amount': 50000,
        'loan_term': 60
    }
    result = predict(sample)
    print("\n=== Prediction Result ===")
    print(f"Decision          : {result['decision']}")
    print(f"Approval Prob     : {result['approval_probability']}%")
    print(f"Risk Score        : {result['risk_score']}")
    print("\nPositive Factors:")
    for p in result['explanations']['positive']:
        print(f"  + {p}")
    print("\nNegative Factors:")
    for n in result['explanations']['negative']:
        print(f"  - {n}")
