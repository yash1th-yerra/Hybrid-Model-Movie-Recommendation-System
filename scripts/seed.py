import os
import pandas as pd
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Movie, Rating, User

app = create_app()

def seed_data():
    with app.app_context():
        # Create tables if they don't exist (though migrate should handle this, good for dev)
        db.create_all()

        if Movie.query.first():
            print("Database already seeded. Skipping...")
            return

        print("Loading Movies...")
        movies_df = pd.read_csv('movies.csv')
        
        # Bulk Insert Movies
        movies_to_insert = []
        for _, row in movies_df.iterrows():
            movie = Movie(
                id=int(row['movieId']),
                title=row['title'],
                genres=row['genres']
            )
            movies_to_insert.append(movie)
        
        db.session.add_all(movies_to_insert)
        db.session.commit()
        print(f"Inserted {len(movies_to_insert)} movies.")

        print("Loading Ratings (this might take a moment)...")
        ratings_df = pd.read_csv('ratings.csv')
        
        # We need to create Users first to satisfy ForeignKey
        unique_user_ids = ratings_df['userId'].unique()
        users_to_insert = []
        print(f"Creating {len(unique_user_ids)} dummy users...")
        for uid in unique_user_ids:
            user = User(
                id=int(uid),
                username=f'user_{uid}',
                email=f'user_{uid}@example.com',
                password_hash='dummy_hash' 
            )
            users_to_insert.append(user)
        
        db.session.add_all(users_to_insert)
        db.session.commit()
        print("Users created.")

        # Bulk Insert Ratings
        # Only take a subset if it's too large for dev, but 2.5MB is fine.
        ratings_to_insert = []
        for _, row in ratings_df.iterrows():
            rating = Rating(
                user_id=int(row['userId']),
                movie_id=int(row['movieId']),
                rating=float(row['rating'])
                # timestamp is omitted for simplicity or could be converted
            )
            ratings_to_insert.append(rating)
        
        # Batch insert for performance
        batch_size = 1000
        for i in range(0, len(ratings_to_insert), batch_size):
            db.session.add_all(ratings_to_insert[i:i+batch_size])
            db.session.commit()
            print(f"Inserted ratings batch {i} to {i+batch_size}")

        print("Seeding Complete!")

if __name__ == '__main__':
    seed_data()
