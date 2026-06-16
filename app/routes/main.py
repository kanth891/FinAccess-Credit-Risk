import json
import sys
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import User, Application

main_bp = Blueprint('main', __name__, url_prefix='/api')


@main_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    applications = Application.query.filter_by(user_id=user_id)\
        .order_by(Application.created_at.desc()).all()

    total = len(applications)
    approved = sum(1 for a in applications if a.decision == 'Approved')
    rejected = total - approved
    recent = [a.to_dict() for a in applications[:5]]

    return jsonify({
        'user': user.to_dict(),
        'total': total,
        'approved': approved,
        'rejected': rejected,
        'approval_rate': round((approved / total * 100), 1) if total > 0 else 0,
        'recent': recent
    }), 200


@main_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Validate and parse inputs
    try:
        input_data = {
            'age': int(data['age']),
            'annual_income': float(data['annual_income']),
            'employment_type': str(data['employment_type']),
            'years_employed': int(data['years_employed']),
            'credit_score': int(data['credit_score']),
            'existing_debt': float(data['existing_debt']),
            'loan_amount': float(data['loan_amount']),
            'loan_term': int(data['loan_term']),
        }
    except (ValueError, KeyError) as e:
        return jsonify({'error': f'Invalid input: {e}'}), 400

    # Validate ranges
    if not (18 <= input_data['age'] <= 80):
        return jsonify({'error': 'Age must be between 18 and 80'}), 400
    if not (300 <= input_data['credit_score'] <= 850):
        return jsonify({'error': 'Credit score must be between 300 and 850'}), 400
    if input_data['employment_type'] not in ['Employed', 'Self-Employed', 'Unemployed']:
        return jsonify({'error': 'Invalid employment type'}), 400

    # Run ML prediction
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from ml.predict import predict
        result = predict(input_data)
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

    # Save to database
    app_record = Application(
        user_id=user_id,
        age=input_data['age'],
        annual_income=input_data['annual_income'],
        employment_type=input_data['employment_type'],
        years_employed=input_data['years_employed'],
        credit_score=input_data['credit_score'],
        existing_debt=input_data['existing_debt'],
        loan_amount=input_data['loan_amount'],
        loan_term=input_data['loan_term'],
        risk_score=result['risk_score'],
        approval_probability=result['approval_probability'],
        decision=result['decision'],
        positive_factors=json.dumps(result['explanations']['positive']),
        negative_factors=json.dumps(result['explanations']['negative'])
    )
    db.session.add(app_record)
    db.session.commit()

    return jsonify({
        'app_id': app_record.id,
        'decision': result['decision'],
        'risk_score': result['risk_score'],
        'approval_probability': result['approval_probability'],
        'explanations': result['explanations']
    }), 201


@main_bp.route('/result/<int:app_id>', methods=['GET'])
@jwt_required()
def result(app_id):
    user_id = int(get_jwt_identity())
    application = Application.query.filter_by(id=app_id, user_id=user_id).first()
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    data = application.to_dict()
    return jsonify({'application': data}), 200


@main_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    applications = Application.query.filter_by(user_id=user_id)\
        .order_by(Application.created_at.desc()).all()

    return jsonify({
        'user': user.to_dict(),
        'applications': [a.to_dict() for a in applications]
    }), 200
