import requests

BASE_URL_AUTH = 'http://127.0.0.1:5000/api/auth'
BASE_URL_MOVIES = 'http://127.0.0.1:5000/api/movies'

def test_movies():
    # 1. Login to get token
    print("Logging in first...")
    login_data = {
        'username': 'newuser123',
        'password': 'securepassword'
    }
    # Note: Ensure newuser123 exists (from previous step) or handle error
    resp = requests.post(f'{BASE_URL_AUTH}/login', json=login_data)
    
    token = None
    if resp.status_code == 200:
        token = resp.json()['access_token']
        print("Got Token.")
    else:
        print("Login failed, make sure user exists (run test_auth.py first or seeding issues).")
        return

    # 2. List Movies (Page 1)
    print("\nTesting List Movies (Page 1)...")
    resp = requests.get(f'{BASE_URL_MOVIES}?page=1&per_page=5')
    print(f"List Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Total Movies: {data['total']}")
        print(f"Movies in page: {len(data['movies'])}")
        first_movie = data['movies'][0]
        print(f"First Movie: {first_movie}")
        movie_id = first_movie['id']
    else:
        print("Failed to list movies")
        return

    # 3. Get Movie Details
    print(f"\nTesting Get Movie {movie_id}...")
    resp = requests.get(f'{BASE_URL_MOVIES}/{movie_id}')
    print(f"Detail Status: {resp.status_code}")
    print(f"Detail JSON: {resp.json()}")

    # 4. Rate Movie
    print(f"\nTesting Rate Movie {movie_id}...")
    headers = {'Authorization': f'Bearer {token}'}
    rating_data = {'rating': 4.5}
    resp = requests.post(f'{BASE_URL_MOVIES}/{movie_id}/rate', json=rating_data, headers=headers)
    print(f"Rate Status: {resp.status_code}")
    print(f"Rate Resp: {resp.json()}")

if __name__ == '__main__':
    test_movies()
