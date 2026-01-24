import requests

BASE_URL = 'http://127.0.0.1:5000/api/auth'

def test_auth():
    # Register
    print("Testing Registration...")
    reg_data = {
        'username': 'newuser123',
        'email': 'newuser123@example.com',
        'password': 'securepassword'
    }
    resp = requests.post(f'{BASE_URL}/register', json=reg_data)
    print(f"Register Status: {resp.status_code}")
    print(f"Register Resp: {resp.json()}")

    # Login
    print("\nTesting Login...")
    login_data = {
        'username': 'newuser123',
        'password': 'securepassword'
    }
    resp = requests.post(f'{BASE_URL}/login', json=login_data)
    print(f"Login Status: {resp.status_code}")
    data = resp.json()
    print(f"Login Resp: {data}")
    
    if 'access_token' in data:
        token = data['access_token']
        
        # Protected Route
        print("\nTesting Protected Route...")
        headers = {'Authorization': f'Bearer {token}'}
        resp = requests.get(f'{BASE_URL}/me', headers=headers)
        print(f"Me Status: {resp.status_code}")
        print(f"Me Resp: {resp.json()}")
    else:
        print("Login failed, skipping protected route test.")

if __name__ == '__main__':
    test_auth()
