import streamlit as st
import requests

# API base URL (Flask app endpoint)
API_BASE_URL = "https://flask-app-mrs.onrender.com"

# Title of the Streamlit app
st.title('Movie Recommendation System')

# Input: Movie Title
user_input = st.text_input('Enter a movie title:', 'Jumanji')

# Input: Number of recommendations
n_recommendations = st.slider('Number of recommendations:', 1, 20, 5)


# Function to fetch recommendations from Flask backend
def get_recommendations(title, n_recommendations_):
    response = requests.get(f"{API_BASE_URL}/recommend",
                            params={'title': title, 'n_recommendations': n_recommendations_})

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching recommendations: {response.status_code}")
        return None


# Function to find the closest movie title
def find_movie(title):
    response = requests.get(f"{API_BASE_URL}/movie_finder", params={'title': title})

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error finding movie: {response.status_code}")
        return None


# When the user submits a movie title
if user_input:
    # Find the closest matching movie title
    movie_info = find_movie(user_input)
    if movie_info:
        st.write(f"Did you mean: **{movie_info['closest_match']}**?")

    # Fetch movie recommendations based on the input title
    recommendations = get_recommendations(user_input, n_recommendations)
    if recommendations:
        st.write(f"**Top {n_recommendations} Recommendations**:")
        for i, movie in enumerate(recommendations['recommended_movies'], 1):
            st.write(f"{i}. {movie}")
