import requests
import random
import string

BASE_URL_V2 = "http://127.0.0.1:8080/api/v2"


# --- Helper to generate random email to avoid conflicts ---
def random_email():
    return f"testuser_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}@example.com"


# --- Test Data ---
user_data_valid = {
    "name": "Test",
    "surname": "UserV2",
    "age": 30,
    "position": "Tester",
    "speciality": "API Testing",
    "address": "Test Address",
    "city_from": "Test City",
    "email": random_email(),
    "password": "testpassword123"
}

user_data_missing_required = {
    "surname": "Incomplete",
    "age": 25
}

user_data_invalid_email_format = {
    "name": "Invalid",
    "surname": "Emailer",
    "email": "notanemail",
    "password": "password123"
}


# --- Tests for UsersListResource (/api/v2/users) ---
def test_create_user_success():
    """Test successful user creation (POST)."""
    print("\n--- test_create_user_success (POST /api/v2/users) ---")
    payload = user_data_valid.copy()
    payload["email"] = random_email()
    print(f"POST {BASE_URL_V2}/users with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/users", json=payload)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    response_data = response.json()
    assert 'id' in response_data, "Response JSON missing 'id'"
    assert 'user' in response_data, "Response JSON missing 'user' object"
    created_user = response_data['user']
    assert created_user['email'] == payload['email']
    assert created_user['name'] == payload['name']
    print(f"User created successfully with ID: {response_data['id']}. User data: {created_user}")

    if 'id' in response_data:
        print(f"DELETE {BASE_URL_V2}/users/{response_data['id']} (cleanup)")
        requests.delete(f"{BASE_URL_V2}/users/{response_data['id']}")
    print("--- test_create_user_success PASSED ---")


def test_create_user_missing_required_fields():
    """Test user creation with missing required fields (POST)."""
    print("\n--- test_create_user_missing_required_fields (POST /api/v2/users) ---")
    print(f"POST {BASE_URL_V2}/users with data: {user_data_missing_required}")
    response = requests.post(f"{BASE_URL_V2}/users", json=user_data_missing_required)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json(), "Error message not found in response"
    print(f"Received 400 for missing required fields as expected. Message: {response.json()['message']}")
    print("--- test_create_user_missing_required_fields PASSED ---")


def test_create_user_duplicate_email():
    """Test user creation with an already existing email (POST)."""
    print("\n--- test_create_user_duplicate_email (POST /api/v2/users) ---")
    # 1. Create a user
    payload1 = user_data_valid.copy()
    payload1["email"] = random_email()
    print(f"POST {BASE_URL_V2}/users (first user) with data: {payload1}")
    response1 = requests.post(f"{BASE_URL_V2}/users", json=payload1)
    assert response1.status_code == 201
    user1_id = response1.json()['id']

    # 2. Try to create another user with the same email
    payload2 = user_data_valid.copy()
    payload2["name"] = "Another Name"
    payload2["email"] = payload1["email"]  # Use the same email
    print(f"POST {BASE_URL_V2}/users (second user, duplicate email) with data: {payload2}")
    response2 = requests.post(f"{BASE_URL_V2}/users", json=payload2)
    assert response2.status_code == 409, f"Expected 409 (Conflict), got {response2.status_code}. Response: {response2.text}"
    assert 'message' in response2.json()
    assert "already exists" in response2.json()['message']
    print(f"Received 409 for duplicate email as expected. Message: {response2.json()['message']}")

    print(f"DELETE {BASE_URL_V2}/users/{user1_id} (cleanup)")
    requests.delete(f"{BASE_URL_V2}/users/{user1_id}")
    print("--- test_create_user_duplicate_email PASSED ---")


def test_get_all_users():
    """Test getting all users (GET)."""
    print("\n--- test_get_all_users (GET /api/v2/users) ---")
    email1 = random_email()
    email2 = random_email()
    user1_payload = {**user_data_valid, "email": email1, "name": "User One"}
    user2_payload = {**user_data_valid, "email": email2, "name": "User Two", "surname": "For Get All"}

    resp1 = requests.post(f"{BASE_URL_V2}/users", json=user1_payload)
    assert resp1.status_code == 201
    id1 = resp1.json()['id']
    resp2 = requests.post(f"{BASE_URL_V2}/users", json=user2_payload)
    assert resp2.status_code == 201
    id2 = resp2.json()['id']

    print(f"GET {BASE_URL_V2}/users")
    response = requests.get(f"{BASE_URL_V2}/users")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    response_data = response.json()
    assert 'users' in response_data, "Response JSON missing 'users' key"
    assert isinstance(response_data['users'], list), "'users' should be a list"
    assert len(response_data['users']) >= 2, "Expected at least 2 users in the list"

    emails_in_response = [user['email'] for user in response_data['users']]
    assert email1 in emails_in_response
    assert email2 in emails_in_response
    print(f"Retrieved list of users. Count: {len(response_data['users'])}")

    requests.delete(f"{BASE_URL_V2}/users/{id1}")
    requests.delete(f"{BASE_URL_V2}/users/{id2}")
    print("--- test_get_all_users PASSED ---")


# --- Tests for UsersResource (/api/v2/users/<int:user_id>) ---
def test_get_one_user_success():
    """Test getting a single existing user (GET)."""
    print("\n--- test_get_one_user_success (GET /api/v2/users/<id>) ---")
    # 1. Create a user
    payload = user_data_valid.copy()
    payload["email"] = random_email()
    print(f"POST {BASE_URL_V2}/users (for GET one) with data: {payload}")
    response_create = requests.post(f"{BASE_URL_V2}/users", json=payload)
    assert response_create.status_code == 201
    user_id = response_create.json()['id']
    print(f"User created with ID: {user_id}")

    # 2. Get the user by ID
    print(f"GET {BASE_URL_V2}/users/{user_id}")
    response_get = requests.get(f"{BASE_URL_V2}/users/{user_id}")
    assert response_get.status_code == 200, f"Expected 200, got {response_get.status_code}. Response: {response_get.text}"
    response_data = response_get.json()
    assert 'user' in response_data, "Response JSON missing 'user' key"
    fetched_user = response_data['user']
    assert fetched_user['id'] == user_id
    assert fetched_user['email'] == payload['email']
    print(f"Retrieved user {user_id} successfully: {fetched_user}")

    print(f"DELETE {BASE_URL_V2}/users/{user_id} (cleanup)")
    requests.delete(f"{BASE_URL_V2}/users/{user_id}")
    print("--- test_get_one_user_success PASSED ---")


def test_get_one_user_not_found():
    """Test getting a non-existent user (GET)."""
    print("\n--- test_get_one_user_not_found (GET /api/v2/users/<id>) ---")
    non_existent_id = 999999
    print(f"GET {BASE_URL_V2}/users/{non_existent_id}")
    response = requests.get(f"{BASE_URL_V2}/users/{non_existent_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json()
    print(f"Received 404 for non-existent user ID as expected. Message: {response.json()['message']}")
    print("--- test_get_one_user_not_found PASSED ---")


def test_delete_user_success():
    """Test successful deletion of an existing user (DELETE)."""
    print("\n--- test_delete_user_success (DELETE /api/v2/users/<id>) ---")
    # 1. Create a user
    payload = user_data_valid.copy()
    payload["email"] = random_email()
    print(f"POST {BASE_URL_V2}/users (for DELETE) with data: {payload}")
    response_create = requests.post(f"{BASE_URL_V2}/users", json=payload)
    assert response_create.status_code == 201
    user_id = response_create.json()['id']
    print(f"User created with ID: {user_id}")

    # 2. Delete the user
    print(f"DELETE {BASE_URL_V2}/users/{user_id}")
    response_delete = requests.delete(f"{BASE_URL_V2}/users/{user_id}")
    assert response_delete.status_code == 200, f"Expected 200, got {response_delete.status_code}. Response: {response_delete.text}"
    assert 'success' in response_delete.json() and response_delete.json()['success'] == 'OK'
    print(f"User {user_id} deleted successfully.")

    # 3. Verify deletion by trying to GET the user
    print(f"GET {BASE_URL_V2}/users/{user_id} (expecting 404)")
    response_get_deleted = requests.get(f"{BASE_URL_V2}/users/{user_id}")
    assert response_get_deleted.status_code == 404, f"User {user_id} was not actually deleted. GET returned {response_get_deleted.status_code}"
    print(f"Confirmed user {user_id} is deleted (GET returned 404).")
    print("--- test_delete_user_success PASSED ---")


def test_delete_user_not_found():
    """Test deleting a non-existent user (DELETE)."""
    print("\n--- test_delete_user_not_found (DELETE /api/v2/users/<id>) ---")
    non_existent_id = 999998
    print(f"DELETE {BASE_URL_V2}/users/{non_existent_id}")
    response = requests.delete(f"{BASE_URL_V2}/users/{non_existent_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json()
    print(f"Received 404 for non-existent user ID deletion as expected. Message: {response.json()['message']}")
    print("--- test_delete_user_not_found PASSED ---")


# --- Tests for PUT (Edit User) - Add these if you implemented PUT in UsersResource ---
def test_edit_user_success():
    """Test successful update of an existing user (PUT)."""
    print("\n--- test_edit_user_success (PUT /api/v2/users/<id>) ---")
    # 1. Create a user
    initial_payload = user_data_valid.copy()
    initial_payload["email"] = random_email()
    print(f"POST {BASE_URL_V2}/users (for PUT) with data: {initial_payload}")
    response_create = requests.post(f"{BASE_URL_V2}/users", json=initial_payload)
    assert response_create.status_code == 201
    user_id = response_create.json()['id']
    print(f"User created with ID: {user_id}")

    # 2. Edit the user
    update_payload = {
        "name": "Updated Name V2",
        "surname": "Updated Surname V2",
        "age": 35,
        "city_from": "Updated City"
    }
    print(f"PUT {BASE_URL_V2}/users/{user_id} with data: {update_payload}")
    response_put = requests.put(f"{BASE_URL_V2}/users/{user_id}", json=update_payload)
    assert response_put.status_code == 200, f"Expected 200, got {response_put.status_code}. Response: {response_put.text}"
    updated_user = response_put.json()['user']
    assert updated_user['name'] == update_payload['name']
    assert updated_user['surname'] == update_payload['surname']
    assert updated_user['age'] == update_payload['age']
    assert updated_user['city_from'] == update_payload['city_from']
    assert updated_user['email'] == initial_payload['email']
    print(f"User {user_id} updated successfully: {updated_user}")

    print(f"DELETE {BASE_URL_V2}/users/{user_id} (cleanup)")
    requests.delete(f"{BASE_URL_V2}/users/{user_id}")
    print("--- test_edit_user_success PASSED ---")


def test_edit_user_change_email_to_existing():
    """Test editing a user's email to an already existing email (PUT)."""
    print("\n--- test_edit_user_change_email_to_existing (PUT /api/v2/users/<id>) ---")
    # 1. Create user1
    email1 = random_email()
    user1_payload = {**user_data_valid, "email": email1, "name": "User One Email"}
    resp1 = requests.post(f"{BASE_URL_V2}/users", json=user1_payload)
    assert resp1.status_code == 201

    # 2. Create user2
    email2 = random_email()
    user2_payload = {**user_data_valid, "email": email2, "name": "User Two Email"}
    resp2 = requests.post(f"{BASE_URL_V2}/users", json=user2_payload)
    assert resp2.status_code == 201
    user2_id = resp2.json()['id']

    # 3. Try to change user2's email to user1's email
    update_payload = {"email": email1}
    print(f"PUT {BASE_URL_V2}/users/{user2_id} with data (duplicate email): {update_payload}")
    response_put = requests.put(f"{BASE_URL_V2}/users/{user2_id}", json=update_payload)
    assert response_put.status_code == 409, f"Expected 409 (Conflict), got {response_put.status_code}. Response: {response_put.text}"
    assert 'message' in response_put.json() and "already exists" in response_put.json()['message']
    print(f"Received 409 when trying to change email to an existing one. Message: {response_put.json()['message']}")

    print(f"DELETE {BASE_URL_V2}/users/{resp1.json()['id']} (cleanup user1)")
    requests.delete(f"{BASE_URL_V2}/users/{resp1.json()['id']}")
    print(f"DELETE {BASE_URL_V2}/users/{user2_id} (cleanup user2)")
    requests.delete(f"{BASE_URL_V2}/users/{user2_id}")
    print("--- test_edit_user_change_email_to_existing PASSED ---")


if __name__ == "__main__":
    print("Running Users API v2 tests...")
    test_create_user_success()
    test_create_user_missing_required_fields()
    test_create_user_duplicate_email()
    test_get_all_users()
    test_get_one_user_success()
    test_get_one_user_not_found()
    test_delete_user_success()
    test_delete_user_not_found()
    test_edit_user_success()
    test_edit_user_change_email_to_existing()
    print("\nAll Users API v2 tests finished.")
