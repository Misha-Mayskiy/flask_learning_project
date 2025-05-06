import requests

BASE_URL = "http://127.0.0.1:8080/api"


# --- Helper function to create a job for testing ---
def create_test_job(job_data):
    print(f"POST {BASE_URL}/jobs with data: {job_data}")
    response = requests.post(f"{BASE_URL}/jobs", json=job_data)
    assert response.status_code == 201, f"Helper: Failed to create job. Status: {response.status_code}, Response: {response.text}"
    created_job_info = response.json()['job']
    print(f"Helper: Job created successfully with ID: {created_job_info['id']}")
    return created_job_info


# --- Helper function to delete a job after testing ---
def delete_test_job(job_id):
    print(f"DELETE {BASE_URL}/jobs/{job_id} (cleanup)")
    response = requests.delete(f"{BASE_URL}/jobs/{job_id}")
    if response.status_code == 204:
        print(f"Helper: Job {job_id} cleaned up successfully.")
    elif response.status_code == 404:
        print(f"Helper: Job {job_id} was already deleted or not found during cleanup.")
    else:
        print(f"Helper: Warning - cleanup for job {job_id} failed or had unexpected status: {response.status_code}")


def test_edit_job_success_partial_update():
    """
    Test successful partial update of an existing job.
    """
    print("\n--- test_edit_job_success_partial_update ---")
    initial_job_data = {
        "job": "Initial Test Job for Edit",
        "team_leader_id": 1,
        "work_size": 15,
        "collaborators": "1,2",
        "is_finished": False,
        "category_ids": []
    }
    created_job = create_test_job(initial_job_data)
    job_id = created_job['id']

    update_payload = {
        "job": "Updated Job Title via API Edit",
        "work_size": 25,
        "is_finished": True
    }
    print(f"PUT {BASE_URL}/jobs/{job_id} with data: {update_payload}")
    response_edit = requests.put(f"{BASE_URL}/jobs/{job_id}", json=update_payload)
    assert response_edit.status_code == 200, f"Edit failed. Status: {response_edit.status_code}, Response: {response_edit.text}"

    edited_job_data = response_edit.json().get('job')
    assert edited_job_data is not None, "Response JSON does not contain 'job' key"
    print(f"Job {job_id} edited successfully. Response: {edited_job_data}")

    assert edited_job_data['job'] == update_payload['job']
    assert edited_job_data['work_size'] == update_payload['work_size']
    assert edited_job_data['is_finished'] == update_payload['is_finished']
    assert edited_job_data['team_leader_id'] == initial_job_data['team_leader_id']
    assert edited_job_data['collaborators'] == initial_job_data['collaborators']
    print("Partial update fields correctly changed, unchanged fields remained.")

    print(f"GET {BASE_URL}/jobs/{job_id} (verifying edit)")
    response_get = requests.get(f"{BASE_URL}/jobs/{job_id}")
    assert response_get.status_code == 200
    fetched_job_data = response_get.json()['job']
    assert fetched_job_data['job'] == update_payload['job']
    assert fetched_job_data['work_size'] == update_payload['work_size']
    assert fetched_job_data['is_finished'] == update_payload['is_finished']
    print("Verification via GET confirmed the changes.")

    delete_test_job(job_id)
    print("--- test_edit_job_success_partial_update PASSED ---")


def test_edit_job_success_update_categories():
    """
    Test successful update of job categories.
    Assumes categories with ID 1 and 2 exist.
    """
    print("\n--- test_edit_job_success_update_categories ---")
    initial_job_data = {
        "job": "Job for Category Edit Test",
        "team_leader_id": 1,
        "work_size": 5,
        "is_finished": False,
        "category_ids": []
    }
    created_job = create_test_job(initial_job_data)
    job_id = created_job['id']

    update_payload_categories = {
        "category_ids": [1, 2]
    }
    print(f"PUT {BASE_URL}/jobs/{job_id} with category data: {update_payload_categories}")
    response_edit_cat = requests.put(f"{BASE_URL}/jobs/{job_id}", json=update_payload_categories)
    assert response_edit_cat.status_code == 200, (f"Category edit failed. "
                                                  f"Status: {response_edit_cat.status_code}, "
                                                  f"Response: {response_edit_cat.text}")

    edited_job_cat_data = response_edit_cat.json().get('job')
    assert edited_job_cat_data is not None
    print(f"Job {job_id} categories edited. Response: {edited_job_cat_data}")

    assert len(edited_job_cat_data['categories']) == 2
    category_ids_in_response = sorted([cat['id'] for cat in edited_job_cat_data['categories']])
    assert category_ids_in_response == [1, 2]
    print("Categories updated correctly.")

    delete_test_job(job_id)
    print("--- test_edit_job_success_update_categories PASSED ---")


def test_edit_non_existent_job():
    """
    Test editing a non-existent job (expect 404).
    """
    print("\n--- test_edit_non_existent_job ---")
    non_existent_job_id = 99998
    update_payload = {"job": "Trying to update non-existent"}
    print(f"PUT {BASE_URL}/jobs/{non_existent_job_id} with data: {update_payload}")
    response = requests.put(f"{BASE_URL}/jobs/{non_existent_job_id}", json=update_payload)
    assert response.status_code == 404, (f"Expected 404 for non-existent job edit,"
                                         f" got {response.status_code}. Response: {response.text}")
    assert 'error' in response.json(), "Error message not found in JSON response"
    print(f"Received 404 for non-existent job ID {non_existent_job_id} as expected.")
    print("--- test_edit_non_existent_job PASSED ---")


def test_edit_job_with_invalid_id_type():
    """
    Test editing a job with an invalid ID type (e.g., string).
    Flask route matching should return 404.
    """
    print("\n--- test_edit_job_with_invalid_id_type ---")
    invalid_job_id = "xyz"
    update_payload = {"job": "Invalid ID type"}
    print(f"PUT {BASE_URL}/jobs/{invalid_job_id} with data: {update_payload}")
    response = requests.put(f"{BASE_URL}/jobs/{invalid_job_id}", json=update_payload)
    assert response.status_code == 404, (f"Expected 404 for invalid ID type edit,"
                                         f" got {response.status_code}. Response: {response.text}")
    print(f"Received 404 for invalid job ID type '{invalid_job_id}' as expected.")
    print("--- test_edit_job_with_invalid_id_type PASSED ---")


def test_edit_job_with_empty_json_body():
    """
    Test editing a job with an empty JSON body (expect 400 if your API requires JSON).
    """
    print("\n--- test_edit_job_with_empty_json_body ---")
    initial_job_data = {"job": "Job for Empty Edit Test", "team_leader_id": 1, "work_size": 1}
    created_job = create_test_job(initial_job_data)
    job_id = created_job['id']

    print(f"PUT {BASE_URL}/jobs/{job_id} with empty JSON: {{}}")
    response = requests.put(f"{BASE_URL}/jobs/{job_id}", json={})
    assert response.status_code == 200, (f"Expected 200 for empty JSON (no fields to update),"
                                         f" got {response.status_code}. Response: {response.text}")
    print(f"Received 200 for job ID {job_id} with empty JSON body as expected (no changes made).")

    delete_test_job(job_id)
    print("--- test_edit_job_with_empty_json_body PASSED ---")


def test_edit_job_with_non_json_body():
    """
    Test editing a job with a non-JSON body (expect 400).
    """
    print("\n--- test_edit_job_with_non_json_body ---")
    initial_job_data = {"job": "Job for Non-JSON Edit Test", "team_leader_id": 1, "work_size": 1}
    created_job = create_test_job(initial_job_data)
    job_id = created_job['id']

    print(f"PUT {BASE_URL}/jobs/{job_id} with non-JSON data")
    response = requests.put(f"{BASE_URL}/jobs/{job_id}", data="this is not json")
    assert response.status_code == 400, (f"Expected 400 for non-JSON body, "
                                         f"got {response.status_code}. Response: {response.text}")
    assert 'error' in response.json(), "Error message not found for non-JSON body"
    assert "Request must be JSON" in response.json()['error'], "Incorrect error message for non-JSON body"
    print(f"Received 400 for job ID {job_id} with non-JSON body as expected.")

    delete_test_job(job_id)  # Cleanup
    print("--- test_edit_job_with_non_json_body PASSED ---")


def test_edit_job_update_with_non_existent_category():
    """
    Test editing a job to include a non-existent category (expect 400).
    """
    print("\n--- test_edit_job_update_with_non_existent_category ---")
    initial_job_data = {"job": "Job for Bad Category Edit", "team_leader_id": 1, "work_size": 1, "category_ids": []}
    created_job = create_test_job(initial_job_data)
    job_id = created_job['id']

    update_payload = {
        "category_ids": [99999]
    }
    print(f"PUT {BASE_URL}/jobs/{job_id} with non-existent category data: {update_payload}")
    response_edit = requests.put(f"{BASE_URL}/jobs/{job_id}", json=update_payload)
    assert response_edit.status_code == 400, (f"Expected 400 for non-existent category,"
                                              f" got {response_edit.status_code}. Response: {response_edit.text}")
    assert 'error' in response_edit.json()
    assert "Category with id 99999 not found" in response_edit.json()['error']
    print("Received 400 due to non-existent category as expected.")

    print(f"GET {BASE_URL}/jobs/{job_id} (verifying no change after failed category update)")
    response_get = requests.get(f"{BASE_URL}/jobs/{job_id}")
    assert response_get.status_code == 200
    fetched_job_data = response_get.json()['job']
    assert len(fetched_job_data['categories']) == 0
    print("Job categories remained unchanged after failed update, as expected.")

    delete_test_job(job_id)
    print("--- test_edit_job_update_with_non_existent_category PASSED ---")


if __name__ == "__main__":
    print("Running Jobs API EDIT tests...")
    test_edit_job_success_partial_update()
    test_edit_job_success_update_categories()  # Need categories 1 & 2 exist
    test_edit_non_existent_job()
    test_edit_job_with_invalid_id_type()
    test_edit_job_with_empty_json_body()
    test_edit_job_with_non_json_body()
    test_edit_job_update_with_non_existent_category()
    print("\nAll edit tests finished.")
