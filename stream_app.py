import streamlit as st
from recommender import HybridRecommender

# Initialize recommender (cached to avoid reloading on every interaction)
@st.cache_resource
def load_recommender():
    return HybridRecommender()

recommender = load_recommender()

# Streamlit App Interface
st.title('Hybrid Movie Recommendation System')

# Input: Movie Title
user_input = st.text_input('Enter a movie title:', 'Jumanji')

# Input: Number of recommendations
n_recommendations = st.slider('Number of recommendations:', 1, 20, 5)

# Function to display recommendations
def display_recommendations(title, n_recommendations_):
    try:
        # Fetch movie recommendations based on the input title
        recommendations = recommender.get_recommendations(title, n_recommendations_)
        
        if recommendations:
            st.write(f"**Top {n_recommendations_} Recommendations**:")
            for i, movie in enumerate(recommendations, 1):
                st.write(f"{i}. {movie}")
        else:
            st.warning("No recommendations found.")
            
    except Exception as e:
        st.error(f"Error: {e}")
        # Fallback closest match logic is handled inside recommender, 
        # but we can also explicity show it if needed.

# Function to find the closest movie title
def display_closest_match(title):
    try:
        closest_match = recommender.movie_finder(title)
        st.write(f"Did you mean: **{closest_match}**?")
    except:
        pass

# When the user submits a movie title
if user_input:
    # Find the closest matching movie title
    display_closest_match(user_input)

    # Fetch movie recommendations based on the input title
    display_recommendations(user_input, n_recommendations)
