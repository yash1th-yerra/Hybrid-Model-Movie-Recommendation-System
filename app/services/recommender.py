import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix
from app.models import Movie, Rating
from app.extensions import db
from sqlalchemy import text

class RecommendationService:
    def __init__(self):
        self.movies_df = None
        self.ratings_df = None
        self.movie_idx = None # Map title -> index (Content)
        self.idx_to_movie = None
        self.cosine_sim_content = None
        self.cosine_sim_collab = None
        self.mapper = None # Map title -> index (Collab)
        self.index_to_title_collab = None
        self.initialized = False

    def load_data(self):
        """Load data from the Database into Pandas DataFrames"""
        # Load Movies
        # using read_sql with db.session.connection()
        conn = db.session.connection()
        
        self.movies_df = pd.read_sql(text("SELECT * FROM movie"), conn)
        self.ratings_df = pd.read_sql(text("SELECT * FROM rating"), conn)
        
        self.movies_df['genres'] = self.movies_df['genres'].fillna('')
        
        # Mapping for Content-Based
        self.movies_df = self.movies_df.reset_index(drop=True)
        # We will use 'title' as the key to match legacy logic, but ID is better in future.
        self.movie_idx = dict(zip(self.movies_df['title'], list(self.movies_df.index)))
        self.idx_to_movie = dict(zip(list(self.movies_df.index), self.movies_df['title']))
        
        self.initialized = True

    def train_models(self):
        if not self.initialized:
            self.load_data()
            
        print("Training Content Model...")
        # Content-Based (Genres)
        count_vectorizer = CountVectorizer(stop_words='english')
        genre_matrix = count_vectorizer.fit_transform(self.movies_df['genres'])
        self.cosine_sim_content = cosine_similarity(genre_matrix, genre_matrix)
        
        print("Training Collaborative Model...")
        # Collaborative (Ratings)
        # Merge not needed if we have IDs, but let's stick to the pivot on Title for consistency with legacy
        # or better, pivot on Movie ID? 
        # The legacy code pivoted on TITLE. Let's try to pivot on Title to keep logic similar.
        
        ratings_with_titles = self.ratings_df.merge(self.movies_df[['id', 'title']], left_on='movie_id', right_on='id')
        user_movie_matrix = ratings_with_titles.pivot_table(index='title', columns='user_id', values='rating').fillna(0)
        
        movie_user_matrix_sparse = csr_matrix(user_movie_matrix.values)
        self.cosine_sim_collab = cosine_similarity(movie_user_matrix_sparse)
        
        self.mapper = {title: i for i, title in enumerate(user_movie_matrix.index)}
        self.index_to_title_collab = {i: title for i, title in enumerate(user_movie_matrix.index)}

    def find_closest_title(self, title):
        """Find the closest matching title using FuzzyWuzzy"""
        if not self.initialized:
            self.train_models()
        
        # If exact match exists, return it
        if title in self.movie_idx:
            return title
            
        # Otherwise find closest
        from fuzzywuzzy import process
        all_titles = list(self.movie_idx.keys())
        match = process.extractOne(title, all_titles)
        # match is (string, score)
        if match and match[1] >= 60: # Threshold
            return match[0]
        return None

    def get_recommendations(self, title_input, n_recommendations=10):
        if not self.initialized:
            self.train_models() # Auto-train on first request if needed
            
        title = self.find_closest_title(title_input)
        
        if not title:
            # If still nothing
            return [] 

        # --- Content-Based ---
        content_scores = {}
        idx = self.movie_idx[title]
        sim_scores = list(enumerate(self.cosine_sim_content[idx]))
        for i, score in sim_scores:
            curr_title = self.idx_to_movie[i]
            content_scores[curr_title] = score
            
        # --- Collaborative ---
        collab_scores = {}
        if title in self.mapper:
            idx = self.mapper[title]
            sim_scores = list(enumerate(self.cosine_sim_collab[idx]))
            for i, score in sim_scores:
                curr_title = self.index_to_title_collab[i]
                collab_scores[curr_title] = score
                
        # --- Hybrid ---
        all_movies = set(content_scores.keys()) | set(collab_scores.keys())
        if title in all_movies:
            all_movies.remove(title)
            
        final_scores = []
        for mv in all_movies:
            s_content = content_scores.get(mv, 0.0)
            s_collab = collab_scores.get(mv, 0.0)
            
            # 50/50 Weight
            hybrid_score = (s_content * 0.5) + (s_collab * 0.5)
            # Store also the matched title to tell the user what we used
            final_scores.append({'title': mv, 'score': hybrid_score})
            
        final_scores = sorted(final_scores, key=lambda x: x['score'], reverse=True)
        return {'matched_title': title, 'recommendations': final_scores[:n_recommendations]}

# Singleton Instance
recommender_service = RecommendationService()
