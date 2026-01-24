import requests

BASE_URL_MOVIES = 'http://127.0.0.1:5000/api/movies'
BASE_URL_REC = 'http://127.0.0.1:5000/api/recommend'

def test_search_and_optimize():
    # 1. Test Search Endpoint
    print("Testing Search 'Jumanji'...")
    resp = requests.get(f'{BASE_URL_MOVIES}/search?q=Jumanji')
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Found {data['count']} results.")
        for m in data['results']:
            print(f" - {m['title']}")
            
    # 2. Test Fuzzy Recommendation
    typo_title = "Jumanji The Jungl" # "Jumanji" or similar
    print(f"\nTesting Recommendation with Typo: '{typo_title}'...")
    try:
        resp = requests.get(f'{BASE_URL_REC}/hybrid?title={typo_title}&limit=3', timeout=30)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Matched: {data.get('matched_movie')}")
            print(f"Recommendations: {[r['title'] for r in data['recommendations']]}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Timeout/Error: {e}")

if __name__ == '__main__':
    test_search_and_optimize()
