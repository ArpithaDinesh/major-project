import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_auth_flow():
    print("=== Testing MindSync Real User Authentication Flow ===")
    
    # 1. Non-existent login
    print("\n1. Testing Login with non-existent user...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "nonexistent_user_xyz@test.com",
        "password": "somepassword123"
    })
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}"
    assert "No account found" in r.json().get("detail", "")
    print("-> PASS: Rejected non-existent user with proper error.")

    # 2. Sign up new user
    import time
    test_email = f"user_{int(time.time())}@example.com"
    test_password = "SecurePassword#99"
    test_name = "Jane Developer"

    print(f"\n2. Testing Sign Up with real credentials: {test_email}...")
    r = requests.post(f"{BASE_URL}/auth/signup", json={
        "name": test_name,
        "email": test_email,
        "password": test_password
    })
    print(f"Status: {r.status_code}")
    data = r.json()
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {data}"
    assert "access_token" in data, "Token missing from signup response"
    assert data["email"] == test_email
    assert data["name"] == test_name
    assert "password_hash" not in data, "password_hash must NOT be leaked"
    token = data["access_token"]
    print(f"-> PASS: Registered successfully in MongoDB Atlas. Received signed JWT: {token[:25]}...")

    # 3. Duplicate Sign Up
    print("\n3. Testing Duplicate Sign Up with same email...")
    r = requests.post(f"{BASE_URL}/auth/signup", json={
        "name": "Jane Developer Duplicate",
        "email": test_email,
        "password": test_password
    })
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 400
    assert "already exists" in r.json().get("detail", "")
    print("-> PASS: Rejected duplicate email registration.")

    # 4. Login with wrong password
    print("\n4. Testing Login with incorrect password...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": "wrong_password_123"
    })
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 401
    assert "Incorrect password" in r.json().get("detail", "")
    print("-> PASS: Rejected incorrect password.")

    # 5. Login with correct password
    print("\n5. Testing Login with correct credentials...")
    r = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    print(f"Status: {r.status_code}")
    login_data = r.json()
    assert r.status_code == 200
    assert "access_token" in login_data
    assert login_data["email"] == test_email
    login_token = login_data["access_token"]
    print(f"-> PASS: Logged in successfully. Token: {login_token[:25]}...")

    # 6. Verify protected /auth/me with Bearer token
    print("\n6. Testing Protected /auth/me endpoint...")
    headers = {"Authorization": f"Bearer {login_token}"}
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {r.status_code}, User: {r.json().get('name')} ({r.json().get('email')})")
    assert r.status_code == 200
    assert r.json()["email"] == test_email
    print("-> PASS: Protected route validated JWT token against MongoDB Atlas.")

    # 7. Verify protected /auth/me without token fails
    print("\n7. Testing Protected /auth/me without token...")
    r = requests.get(f"{BASE_URL}/auth/me")
    print(f"Status: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 401
    print("-> PASS: Unauthenticated access rejected.")

    print("\nALL AUTHENTICATION TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_auth_flow()
