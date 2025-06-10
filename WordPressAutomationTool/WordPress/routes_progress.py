from flask import jsonify, request
from flask_login import current_user
from app_init import app
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """Custom login required decorator that works with app structure"""
    return f

@app.route('/api/save_progress', methods=['POST'])
@login_required
def save_progress():
    """Save user's current stage progress"""
    try:
        data = request.get_json()
        stage = data.get('stage')
        stage_data = data.get('data', {})

        if not stage or not isinstance(stage, int) or stage < 1 or stage > 10:
            return jsonify({'error': 'Invalid stage number'}), 400

        # Get user's active subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).order_by(SubscriptionPlan.id.desc()).first()

        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404

        # Update progress
        subscription.current_stage = stage
        subscription.stage_data = stage_data
        db.session.commit()

        logger.info(f"Progress saved for user {current_user.id} at stage {stage}")
        return jsonify({'message': 'Progress saved successfully'})

    except Exception as e:
        logger.error(f"Error saving progress: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/resume_progress', methods=['GET'])
@login_required
def resume_progress():
    """Get user's saved progress"""
    try:
        # Get user's active subscription
        subscription = SubscriptionPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).order_by(SubscriptionPlan.id.desc()).first()

        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404

        progress = {
            'current_stage': subscription.current_stage,
            'stage_data': subscription.stage_data or {}
        }

        return jsonify(progress)

    except Exception as e:
        logger.error(f"Error retrieving progress: {e}")
        return jsonify({'error': 'Internal server error'}), 500