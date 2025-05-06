import requests
import random
import string
import datetime

BASE_URL_V2 = "http://127.0.0.1:8080/api/v2"


# --- Helper to generate random string for job titles ---
def random_job_title():
    return f"Test Job {''.join(random.choices(string.ascii_letters + string.digits, k=10))}"


# --- Helper to get current time in ISO format for dates (optional) ---
def current_iso_time():
    return datetime.datetime.now().isoformat()


# --- Test Data ---
valid_job_payload = {
    "job": random_job_title(),
    "team_leader_id": 1,
    "work_size": 20,
    "collaborators": "2,3",
    "is_finished": False,
    "start_date": current_iso_time(),
    "category_ids": [1]
}


# --- Tests for JobsListResource (/api/v2/jobs) ---
def test_create_job_success():
    """Test successful job creation."""
    print("\n--- test_create_job_success (POST /api/v2/jobs) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["start_date"] = current_iso_time()
    print(f"POST {BASE_URL_V2}/jobs with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/jobs", json=payload)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    response_data = response.json()
    assert 'id' in response_data, "Response JSON missing 'id'"
    assert 'job' in response_data, "Response JSON missing 'job' object"
    created_job = response_data['job']
    assert created_job['job'] == payload['job']
    assert created_job['team_leader_id'] == payload['team_leader_id']
    assert len(created_job['categories']) == len(payload['category_ids'])
    print(f"Job created successfully with ID: {response_data['id']}. Job data: {created_job}")

    if 'id' in response_data:
        print(f"DELETE {BASE_URL_V2}/jobs/{response_data['id']} (cleanup)")
        requests.delete(f"{BASE_URL_V2}/jobs/{response_data['id']}")
    print("--- test_create_job_success PASSED ---")


def test_create_job_missing_required_fields():
    """Test job creation with missing required fields."""
    print("\n--- test_create_job_missing_required_fields (POST /api/v2/jobs) ---")
    payload = {"work_size": 10}
    print(f"POST {BASE_URL_V2}/jobs with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json(), "Error message not found in response"
    print(f"Received 400 for missing required fields. Message: {response.json()['message']}")
    print("--- test_create_job_missing_required_fields PASSED ---")


def test_create_job_non_existent_team_leader():
    """Test job creation with a non-existent team leader ID."""
    print("\n--- test_create_job_non_existent_team_leader (POST /api/v2/jobs) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["team_leader_id"] = 99999
    print(f"POST {BASE_URL_V2}/jobs with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json() and "Team leader with id 99999 not found" in response.json()['message']
    print(f"Received 400 for non-existent team leader. Message: {response.json()['message']}")
    print("--- test_create_job_non_existent_team_leader PASSED ---")


def test_create_job_non_existent_category():
    """Test job creation with a non-existent category ID."""
    print("\n--- test_create_job_non_existent_category (POST /api/v2/jobs) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["category_ids"] = [99998]
    print(f"POST {BASE_URL_V2}/jobs with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json() and "Category with id 99998 not found" in response.json()['message']
    print(f"Received 400 for non-existent category. Message: {response.json()['message']}")
    print("--- test_create_job_non_existent_category PASSED ---")


def test_create_job_invalid_date_format():
    """Test job creation with invalid date format."""
    print("\n--- test_create_job_invalid_date_format (POST /api/v2/jobs) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["start_date"] = "неверная дата"
    print(f"POST {BASE_URL_V2}/jobs with data: {payload}")
    response = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert response.status_code == 400, f"Expected 400 for invalid date, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json() and "Invalid start_date format" in response.json()['message']
    print(f"Received 400 for invalid date format. Message: {response.json()['message']}")
    print("--- test_create_job_invalid_date_format PASSED ---")


def test_get_all_jobs():
    """Test getting all jobs."""
    print("\n--- test_get_all_jobs (GET /api/v2/jobs) ---")
    job_to_check_payload = valid_job_payload.copy()
    job_to_check_payload["job"] = random_job_title()
    job_to_check_payload["start_date"] = current_iso_time()
    resp_create = requests.post(f"{BASE_URL_V2}/jobs", json=job_to_check_payload)
    assert resp_create.status_code == 201
    created_id = resp_create.json()['id']

    print(f"GET {BASE_URL_V2}/jobs")
    response = requests.get(f"{BASE_URL_V2}/jobs")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    response_data = response.json()
    assert 'jobs' in response_data, "Response JSON missing 'jobs' key"
    assert isinstance(response_data['jobs'], list), "'jobs' should be a list"
    assert len(response_data['jobs']) >= 1, "Expected at least one job in the list"
    found = any(job['id'] == created_id for job in response_data['jobs'])
    assert found, f"Created job with ID {created_id} not found in the list"
    print(f"Retrieved list of jobs. Count: {len(response_data['jobs'])}")

    requests.delete(f"{BASE_URL_V2}/jobs/{created_id}")
    print("--- test_get_all_jobs PASSED ---")


# --- Tests for JobsResource (/api/v2/jobs/<int:job_id>) ---
def test_get_one_job_success():
    """Test getting a single existing job."""
    print("\n--- test_get_one_job_success (GET /api/v2/jobs/<id>) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["start_date"] = current_iso_time()
    resp_create = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert resp_create.status_code == 201
    job_id = resp_create.json()['id']
    print(f"Job created for GET test with ID: {job_id}")

    print(f"GET {BASE_URL_V2}/jobs/{job_id}")
    response_get = requests.get(f"{BASE_URL_V2}/jobs/{job_id}")
    assert response_get.status_code == 200, f"Expected 200, got {response_get.status_code}. Response: {response_get.text}"
    response_data = response_get.json()
    assert 'job' in response_data, "Response JSON missing 'job' key"
    fetched_job = response_data['job']
    assert fetched_job['id'] == job_id
    assert fetched_job['job'] == payload['job']
    print(f"Retrieved job {job_id} successfully: {fetched_job}")

    requests.delete(f"{BASE_URL_V2}/jobs/{job_id}")
    print("--- test_get_one_job_success PASSED ---")


def test_get_one_job_not_found():
    """Test getting a non-existent job."""
    print("\n--- test_get_one_job_not_found (GET /api/v2/jobs/<id>) ---")
    non_existent_id = 999999
    print(f"GET {BASE_URL_V2}/jobs/{non_existent_id}")
    response = requests.get(f"{BASE_URL_V2}/jobs/{non_existent_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json() and f"Job {non_existent_id} not found" in response.json()['message']
    print(f"Received 404 for non-existent job ID as expected. Message: {response.json()['message']}")
    print("--- test_get_one_job_not_found PASSED ---")


def test_delete_job_success():
    """Test successful deletion of an existing job."""
    print("\n--- test_delete_job_success (DELETE /api/v2/jobs/<id>) ---")
    payload = valid_job_payload.copy()
    payload["job"] = random_job_title()
    payload["start_date"] = current_iso_time()
    resp_create = requests.post(f"{BASE_URL_V2}/jobs", json=payload)
    assert resp_create.status_code == 201
    job_id = resp_create.json()['id']
    print(f"Job created for DELETE test with ID: {job_id}")

    print(f"DELETE {BASE_URL_V2}/jobs/{job_id}")
    response_delete = requests.delete(f"{BASE_URL_V2}/jobs/{job_id}")
    assert response_delete.status_code == 200, f"Expected 200, got {response_delete.status_code}. Response: {response_delete.text}"
    assert 'success' in response_delete.json() and response_delete.json()['success'] == 'OK'
    print(f"Job {job_id} deleted successfully.")

    print(f"GET {BASE_URL_V2}/jobs/{job_id} (expecting 404 after delete)")
    response_get_deleted = requests.get(f"{BASE_URL_V2}/jobs/{job_id}")
    assert response_get_deleted.status_code == 404
    print(f"Confirmed job {job_id} is deleted (GET returned 404).")
    print("--- test_delete_job_success PASSED ---")


def test_delete_job_not_found():
    """Test deleting a non-existent job."""
    print("\n--- test_delete_job_not_found (DELETE /api/v2/jobs/<id>) ---")
    non_existent_id = 999998
    print(f"DELETE {BASE_URL_V2}/jobs/{non_existent_id}")
    response = requests.delete(f"{BASE_URL_V2}/jobs/{non_existent_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    assert 'message' in response.json() and f"Job {non_existent_id} not found" in response.json()['message']
    print(f"Received 404 for non-existent job ID deletion. Message: {response.json()['message']}")
    print("--- test_delete_job_not_found PASSED ---")


# --- Тесты для PUT (редактирование) ---
def test_edit_job_success_partial_update():
    """Test successful partial update of an existing job."""
    print("\n--- test_edit_job_success_partial_update (PUT /api/v2/jobs/<id>) ---")
    initial_job_data = valid_job_payload.copy()
    initial_job_data["job"] = random_job_title()
    initial_job_data["start_date"] = current_iso_time()
    created_job_resp = requests.post(f"{BASE_URL_V2}/jobs", json=initial_job_data)
    assert created_job_resp.status_code == 201
    job_id = created_job_resp.json()['id']
    print(f"Job created for PUT test with ID: {job_id}")

    update_payload = {
        "job": "UPDATED " + random_job_title(),
        "work_size": 50,
        "is_finished": True
    }
    print(f"PUT {BASE_URL_V2}/jobs/{job_id} with data: {update_payload}")
    response_edit = requests.put(f"{BASE_URL_V2}/jobs/{job_id}", json=update_payload)
    assert response_edit.status_code == 200, f"Edit failed. Status: {response_edit.status_code}, Response: {response_edit.text}"

    edited_job_data = response_edit.json().get('job')
    assert edited_job_data is not None
    assert edited_job_data['job'] == update_payload['job']
    assert edited_job_data['work_size'] == update_payload['work_size']
    assert edited_job_data['is_finished'] == update_payload['is_finished']
    assert edited_job_data['team_leader_id'] == initial_job_data['team_leader_id']
    assert edited_job_data['collaborators'] == initial_job_data['collaborators']
    print(f"Job {job_id} edited successfully. Partial update verified.")

    requests.delete(f"{BASE_URL_V2}/jobs/{job_id}")
    print("--- test_edit_job_success_partial_update PASSED ---")


def test_edit_job_change_categories():
    """Test changing categories of an existing job."""
    print("\n--- test_edit_job_change_categories (PUT /api/v2/jobs/<id>) ---")
    initial_job_data = {**valid_job_payload, "job": random_job_title(), "category_ids": [1],
                        "start_date": current_iso_time()}
    created_job_resp = requests.post(f"{BASE_URL_V2}/jobs", json=initial_job_data)
    assert created_job_resp.status_code == 201
    job_id = created_job_resp.json()['id']
    print(f"Job created for category PUT test with ID: {job_id}, initial categories: {[1]}")

    update_payload = {"category_ids": [2]}
    print(f"PUT {BASE_URL_V2}/jobs/{job_id} with category data: {update_payload}")
    response_edit = requests.put(f"{BASE_URL_V2}/jobs/{job_id}", json=update_payload)
    assert response_edit.status_code == 200, f"Category edit failed. Status: {response_edit.status_code}, Response: {response_edit.text}"

    edited_job_data = response_edit.json().get('job')
    assert edited_job_data is not None
    assert len(edited_job_data['categories']) == 1
    assert edited_job_data['categories'][0]['id'] == 2
    print(f"Job {job_id} categories changed successfully to: {[cat['id'] for cat in edited_job_data['categories']]}")

    update_payload_empty_cat = {"category_ids": []}
    print(f"PUT {BASE_URL_V2}/jobs/{job_id} with empty category data: {update_payload_empty_cat}")
    response_edit_empty = requests.put(f"{BASE_URL_V2}/jobs/{job_id}", json=update_payload_empty_cat)
    assert response_edit_empty.status_code == 200
    edited_job_empty_cat = response_edit_empty.json().get('job')
    assert len(edited_job_empty_cat['categories']) == 0
    print(f"Job {job_id} categories cleared successfully.")

    requests.delete(f"{BASE_URL_V2}/jobs/{job_id}")
    print("--- test_edit_job_change_categories PASSED ---")


def test_edit_job_non_existent_category_in_update():
    """Test editing a job to include a non-existent category."""
    print("\n--- test_edit_job_non_existent_category_in_update (PUT /api/v2/jobs/<id>) ---")
    initial_job_data = {**valid_job_payload, "job": random_job_title(), "category_ids": [],
                        "start_date": current_iso_time()}
    created_job_resp = requests.post(f"{BASE_URL_V2}/jobs", json=initial_job_data)
    assert created_job_resp.status_code == 201
    job_id = created_job_resp.json()['id']
    print(f"Job created for bad category PUT test with ID: {job_id}")

    update_payload = {"category_ids": [99997]}
    print(f"PUT {BASE_URL_V2}/jobs/{job_id} with non-existent category data: {update_payload}")
    response_edit = requests.put(f"{BASE_URL_V2}/jobs/{job_id}", json=update_payload)
    assert response_edit.status_code == 400, f"Expected 400, got {response_edit.status_code}. Response: {response_edit.text}"
    assert 'message' in response_edit.json() and "Category with id 99997 not found" in response_edit.json()['message']
    print(f"Received 400 for non-existent category in update. Message: {response_edit.json()['message']}")

    requests.delete(f"{BASE_URL_V2}/jobs/{job_id}")
    print("--- test_edit_job_non_existent_category_in_update PASSED ---")


if __name__ == "__main__":
    print("Running Jobs API v2 tests...")
    test_create_job_success()
    test_create_job_missing_required_fields()
    test_create_job_non_existent_team_leader()
    test_create_job_non_existent_category()
    test_create_job_invalid_date_format()
    test_get_all_jobs()
    test_get_one_job_success()
    test_get_one_job_not_found()
    test_delete_job_success()
    test_delete_job_not_found()
    test_edit_job_success_partial_update()
    test_edit_job_change_categories()
    test_edit_job_non_existent_category_in_update()
    print("\nAll Jobs API v2 tests finished.")
