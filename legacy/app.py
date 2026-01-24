from flask import Flask, request, jsonify
from recommender import HybridRecommender

# Create Flask app
app = Flask(__name__)

# Initialize Recommender
recommender = HybridRecommender()

@app.route('/')
def home():
    return 'Welcome to the Hybrid Movie Recommendation API! Use /recommend to get movie recommendations.'


@app.route('/recommend', methods=['GET'])
def recommend_movies():
    title = request.args.get('title', default='Jumanji', type=str)
    n_recommendations = request.args.get('n_recommendations', default=5, type=int)

    try:
        recommendations = recommender.get_recommendations(title, n_recommendations)
        return jsonify({
            'input_movie': title,
            'recommended_movies': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/movie_finder', methods=['GET'])
def find_movie():
    title = request.args.get('title', default='Jumanji', type=str)
    try:
        closest_match = recommender.movie_finder(title)
        return jsonify({
            'input_title': title,
            'closest_match': closest_match
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
