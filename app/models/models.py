from app import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Input features
    age = db.Column(db.Integer, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)
    years_employed = db.Column(db.Integer, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    existing_debt = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)

    # ML output
    risk_score = db.Column(db.Integer, nullable=False)
    approval_probability = db.Column(db.Integer, nullable=False)
    decision = db.Column(db.String(20), nullable=False)

    # SHAP explanations (stored as JSON string)
    positive_factors = db.Column(db.Text, default='[]')
    negative_factors = db.Column(db.Text, default='[]')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'age': self.age,
            'annual_income': self.annual_income,
            'employment_type': self.employment_type,
            'years_employed': self.years_employed,
            'credit_score': self.credit_score,
            'existing_debt': self.existing_debt,
            'loan_amount': self.loan_amount,
            'loan_term': self.loan_term,
            'risk_score': self.risk_score,
            'approval_probability': self.approval_probability,
            'decision': self.decision,
            'positive_factors': json.loads(self.positive_factors or '[]'),
            'negative_factors': json.loads(self.negative_factors or '[]'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }
