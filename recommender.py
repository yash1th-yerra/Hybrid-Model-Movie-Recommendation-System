import pandas as pd
from fuzzywuzzy import process
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix

class HybridRecommender:
    def __init__(self, movie_path='movies.csv', rating_path='ratings.csv'):
        self.movie_path = movie_path
        self.rating_path = rating_path
        self.movies = None
        self.ratings = None
        self.movie_idx = None
        self.idx_to_movie = None
        self.cosine_sim_content = None
        self.cosine_sim_collab = None
        self.mapper = None # Maps movie title to matrix index for collab
        self.index_to_title_collab = None # Maps matrix index to movie title for collab

        self.load_data()
        self.prepare_content_model()
        self.prepare_collaborative_model()

    def load_data(self):
        """Load movies and ratings data."""
        self.movies = pd.read_csv(self.movie_path)
        self.ratings = pd.read_csv(self.rating_path)
        
        # Create a movie index mapping (maps movie titles to indices for content-based)
        # We need to ensure titles are unique or handle duplicates. 
        # For simplicity, we'll take the first occurrence if duplicates exist, or just use the index.
        # The original code acted on the dataframe index.
        self.movies = self.movies.reset_index(drop=True)
        self.movie_idx = dict(zip(self.movies['title'], list(self.movies.index)))
        self.idx_to_movie = dict(zip(list(self.movies.index), self.movies['title']))

    def movie_finder(self, title):
        """Fuzzy match movie title."""
        all_titles = self.movies['title'].tolist()
        closest_match = process.extractOne(title, all_titles)
        return closest_match[0]

    def prepare_content_model(self):
        """Precompute the content-based similarity matrix (Genres)."""
        # Generate a "genre vector" for each movie
        # Fill NaN genres just in case, though usually 'no genres listed'
        self.movies['genres'] = self.movies['genres'].fillna('')
        
        count_vectorizer = CountVectorizer(stop_words='english')
        genre_matrix = count_vectorizer.fit_transform(self.movies['genres'])

        # Compute cosine similarity matrix based on genres
        self.cosine_sim_content = cosine_similarity(genre_matrix, genre_matrix)

    def prepare_collaborative_model(self):
        """Precompute the item-item collaborative similarity matrix (User Ratings)."""
        # Merge ratings with movies to get titles
        ratings_with_titles = self.ratings.merge(self.movies[['movieId', 'title']], on='movieId')
        
        # Pivot the ratings table: Rows = Movies, Cols = Users, Values = Ratings
        user_movie_matrix = ratings_with_titles.pivot_table(index='title', columns='userId', values='rating').fillna(0)
        
        # Convert to sparse matrix for efficiency
        movie_user_matrix_sparse = csr_matrix(user_movie_matrix.values)
        
        # Calculate Cosine Similarity between MOVIES (Item-Item)
        self.cosine_sim_collab = cosine_similarity(movie_user_matrix_sparse)
        
        # We need a new mapping because the pivot table might sort titles differently or exclude movies with no ratings
        self.mapper = {title: i for i, title in enumerate(user_movie_matrix.index)}
        self.index_to_title_collab = {i: title for i, title in enumerate(user_movie_matrix.index)}

    def get_recommendations(self, title_string, n_recommendations=10):
        """
        Get hybrid recommendations.
        Currently defaults to 50/50 weighted split if both exist, 
        or falls back to one if the other is missing.
        """
        fuzzy_title = self.movie_finder(title_string)
        
        # --- Content-Based Recommendations ---
        content_scores = {}
        if fuzzy_title in self.movie_idx:
            idx = self.movie_idx[fuzzy_title]
            sim_scores = list(enumerate(self.cosine_sim_content[idx]))
            # Normalize or just keep raw cosine scores (0 to 1)
            # Store as {title: score}
            for i, score in sim_scores:
                curr_title = self.idx_to_movie[i]
                content_scores[curr_title] = score
        
        # --- Collaborative Recommendations ---
        collab_scores = {}
        if fuzzy_title in self.mapper:
            idx = self.mapper[fuzzy_title]
            sim_scores = list(enumerate(self.cosine_sim_collab[idx]))
            for i, score in sim_scores:
                curr_title = self.index_to_title_collab[i]
                collab_scores[curr_title] = score
        
        # --- Hybrid Fusion ---
        # Combine scores for all unique movies found in either set
        # If a movie is in one but not the other, assume 0 similarity for the missing one? 
        # Or better, just average them.
        
        all_movies = set(content_scores.keys()) | set(collab_scores.keys())
        if fuzzy_title in all_movies:
            all_movies.remove(fuzzy_title) # Remove the input movie itself
            
        final_scores = []
        for mv in all_movies:
            s_content = content_scores.get(mv, 0.0)
            s_collab = collab_scores.get(mv, 0.0)
            
            # Weighted Average: 50% Content, 50% Collaborative
            # We can tune this. Collaborative is usually stronger for "quality", 
            # Content is better for "similarity".
            hybrid_score = (s_content * 0.5) + (s_collab * 0.5)
            final_scores.append((mv, hybrid_score))
            
        # Sort and return top N
        final_scores = sorted(final_scores, key=lambda x: x[1], reverse=True)
        top_n = final_scores[:n_recommendations]
        
        return [x[0] for x in top_n]

if __name__ == "__main__":
    # Simple test
    recommender = HybridRecommender()
    print("Testing Recommender with 'Jumanji'...")
    recs = recommender.get_recommendations('Jumanji', 5)
    print("Recommendations:", recs)
