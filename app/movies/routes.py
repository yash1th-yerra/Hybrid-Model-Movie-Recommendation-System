from flask import Blueprint, request, jsonify
from app.models import Movie, Rating
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

bp = Blueprint('movies', __name__, url_prefix='/api/movies')

@bp.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '', type=str)
    if not query or len(query) < 2:
        return jsonify({'error': 'Search query must be at least 2 characters'}), 400
        
    # SQL based case-insensitive search
    # Using 'ilike' for PostgreSQL, but for SQLite 'like' is case-insensitive by default usually, 
    # but SQLAlchemy 'ilike' handles it cross-db.
    results = Movie.query.filter(Movie.title.ilike(f'%{query}%')).limit(20).all()
    
    movies_data = []
    for movie in results:
        movies_data.append({
            'id': movie.id,
            'title': movie.title,
            'genres': movie.genres
        })
        
    return jsonify({
        'query': query,
        'count': len(movies_data),
        'results': movies_data
    }), 200

@bp.route('', methods=['GET'])
def get_movies():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if per_page > 100:
        per_page = 100
        
    pagination = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    
    movies_data = []
    for movie in pagination.items:
        movies_data.append({
            'id': movie.id,
            'title': movie.title,
            'genres': movie.genres
        })
        
    return jsonify({
        'movies': movies_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'next_page': pagination.next_num,
        'prev_page': pagination.prev_num
    }), 200

@bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return jsonify({
        'id': movie.id,
        'title': movie.title,
        'genres': movie.genres
    }), 200

@bp.route('/<int:movie_id>/rate', methods=['POST'])
@jwt_required()
def rate_movie(movie_id):
    current_user_id = get_jwt_identity()
    movie = Movie.query.get_or_404(movie_id)
    
    data = request.get_json()
    if not data or 'rating' not in data:
        return jsonify({'error': 'Rating value is required'}), 400
        
    score = data['rating']
    try:
        score = float(score)
    except ValueError:
        return jsonify({'error': 'Rating must be a number'}), 400
        
    if not (0.5 <= score <= 5.0):
        return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400
        
    existing_rating = Rating.query.filter_by(user_id=current_user_id, movie_id=movie_id).first()
    
    if existing_rating:
        existing_rating.rating = score
        existing_rating.timestamp = datetime.utcnow()
        message = 'Rating updated'
    else:
        new_rating = Rating(user_id=current_user_id, movie_id=movie_id, rating=score)
        db.session.add(new_rating)
        message = 'Rating submitted'
        
    db.session.commit()
    
    return jsonify({'message': message, 'movie_id': movie_id, 'rating': score}), 200
