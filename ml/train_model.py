import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Paths
ML_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(ML_DIR, '..', 'dataset', 'loan_data.csv')
MODEL_PATH = os.path.join(ML_DIR, 'model.pkl')

EMPLOYMENT_MAP = {'Employed': 2, 'Self-Employed': 1, 'Unemployed': 0}
FEATURE_COLS = ['age', 'annual_income', 'employment_type', 'years_employed',
                'credit_score', 'existing_debt', 'loan_amount', 'loan_term']


def train_model():
    """Train a RandomForestClassifier on the loan dataset and save model.pkl."""
    print("[Training] Loading dataset...")

    # Auto-generate dataset if missing
    if not os.path.exists(DATASET_PATH):
        print("[Training] Dataset not found. Generating...")
        sys.path.insert(0, ML_DIR)
        from generate_dataset import generate_dataset
        generate_dataset()

    df = pd.read_csv(DATASET_PATH)
    print(f"[Training] Dataset loaded: {len(df)} rows")

    # Encode categorical
    df['employment_type'] = df['employment_type'].map(EMPLOYMENT_MAP).fillna(0).astype(int)

    X = df[FEATURE_COLS]
    y = df['approval_status']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train RandomForest
    print("[Training] Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[Training] Accuracy: {acc:.4f}")
    print("[Training] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Rejected', 'Approved']))

    # Save model with feature columns
    model_data = {
        'model': model,
        'feature_cols': FEATURE_COLS,
        'employment_map': EMPLOYMENT_MAP
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model_data, f)

    print(f"[Training] Model saved to: {MODEL_PATH}")
    return model_data


if __name__ == '__main__':
    if os.path.exists(MODEL_PATH):
        print(f"[Training] Model already exists at: {MODEL_PATH}")
        print("[Training] Delete model.pkl to retrain.")
    else:
        train_model()
