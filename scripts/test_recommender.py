import requests

BASE_URL = 'http://127.0.0.1:5000/api/recommend'

def test_recommendation():
    # input_title = "Toyota Story" # Typo? Logic currently handles exact.
    input_title = "Toy Story (1995)"
    
    print(f"Requesting recommendations for: {input_title}")
    # Note: First request will be slow (training models)
    try:
        resp = requests.get(f'{BASE_URL}/hybrid?title={input_title}&limit=5', timeout=30) 
        
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Input: {data['input_movie']}")
            print("Recommendations:")
            for rec in data['recommendations']:
                print(f" - {rec['title']} (Score: {rec['score']:.4f})")
        else:
            print(f"Error: {resp.text}")
            
    except requests.exceptions.ReadTimeout:
        print("Request timed out (Model training took too long?)")

if __name__ == '__main__':
    test_recommendation()
