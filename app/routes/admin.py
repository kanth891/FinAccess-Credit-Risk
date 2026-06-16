from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.models import User, Application
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def get_admin_user():
    """Return user if admin, else None."""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if user and user.is_admin:
            return user
    except Exception:
        pass
    return None


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def admin_stats():
    admin = get_admin_user()
    if not admin:
        return jsonify({'error': 'Admin access required'}), 403

    total_users = User.query.filter_by(is_admin=False).count()
    total_apps = Application.query.count()
    approved = Application.query.filter_by(decision='Approved').count()
    rejected = Application.query.filter_by(decision='Rejected').count()
    approval_rate = round((approved / total_apps * 100), 1) if total_apps > 0 else 0

    all_apps = Application.query.all()
    avg_risk = round(sum(a.risk_score for a in all_apps) / len(all_apps), 1) if all_apps else 0

    return jsonify({
        'total_users': total_users,
        'total_apps': total_apps,
        'approved': approved,
        'rejected': rejected,
        'approval_rate': approval_rate,
        'avg_risk': avg_risk
    }), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def admin_users():
    admin = get_admin_user()
    if not admin:
        return jsonify({'error': 'Admin access required'}), 403

    users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return jsonify({
        'users': [
            {
                **u.to_dict(),
                'application_count': len(u.applications)
            }
            for u in users
        ]
    }), 200


@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def admin_applications():
    admin = get_admin_user()
    if not admin:
        return jsonify({'error': 'Admin access required'}), 403

    apps = Application.query.order_by(Application.created_at.desc()).limit(20).all()
    result = []
    for a in apps:
        d = a.to_dict()
        d['user_name'] = a.user.name if a.user else 'Unknown'
        result.append(d)

    return jsonify({'applications': result}), 200
