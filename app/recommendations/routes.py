from flask import Blueprint, request, jsonify
from app.services.recommender import recommender_service
from app.models import Movie # For searching if needed

bp = Blueprint('recommendations', __name__, url_prefix='/api/recommend')

@bp.before_app_request
def initialize_recommender():
    # Lazy initialization logic could go here, or just let the first request handle it.
    pass

@bp.route('/hybrid', methods=['GET'])
def recommend_hybrid():
    title = request.args.get('title')
    limit = request.args.get('limit', 10, type=int)
    
    if not title:
        return jsonify({'error': 'Title parameter is required'}), 400

    try:
        # Trigger training if not ready (Note: in production this happens at startup or background)
        if not recommender_service.initialized:
            recommender_service.train_models()
            
        recommendations = recommender_service.get_recommendations(title, limit)
        
        return jsonify({
            'input_movie': title,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
