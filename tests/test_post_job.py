import requests
import json
import random

BASE_URL = "http://127.0.0.1:8080/api/jobs"


def pretty_print_json(data):
    """Helper function to print JSON nicely."""
    print(json.dumps(data, indent=4, ensure_ascii=False))


VALID_TEAM_LEADER_ID = 1
VALID_CATEGORY_IDS = [1, 2]
NON_EXISTENT_CATEGORY_ID = 99999


# --- Test Functions ---

def test_post_job_correct():
    print("--- 1. Testing: POST Job - Correct Request ---")
    unique_job_title = f"API Test Job - Correct - {random.randint(1000, 9999)}"
    payload = {
        "job": unique_job_title,
        "team_leader_id": VALID_TEAM_LEADER_ID,
        "work_size": 15,
        "collaborators": "10, 11, 12",
        "is_finished": False,
        "category_ids": VALID_CATEGORY_IDS
    }
    new_job_id = None
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status Code: {response.status_code}")  # Expected: 201
        response.raise_for_status()  # Will raise an exception for 4xx or 5xx
        print("Response JSON:")
        response_data = response.json()
        pretty_print_json(response_data)
        if 'job' in response_data and 'id' in response_data['job']:
            new_job_id = response_data['job']['id']
            print(f"Successfully created job with ID: {new_job_id}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code from error: {e.response.status_code}")
            try:
                print(f"Response Content: {e.response.text}")
            except Exception:
                pass
    print("-" * 30 + "\n")
    return new_job_id  # Return the ID of the created job for later verification


def test_post_job_missing_required_field():
    print("--- 2. Testing: POST Job - Incorrect: Missing 'job' (required field) ---")
    # 'job' is a required field as defined in your API
    payload = {
        # "job": "This field is missing", # Intentionally missing
        "team_leader_id": VALID_TEAM_LEADER_ID,
        "work_size": 10
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status Code: {response.status_code}")  # Expected: 400
        print("Response JSON (or error message):")
        try:
            pretty_print_json(response.json())
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    print("-" * 30 + "\n")


def test_post_job_empty_or_not_json():
    print("--- 3. Testing: POST Job - Incorrect: Empty request body ---")
    # Sending no JSON data or data that isn't JSON
    try:
        # Test 3a: Empty JSON body
        response_empty_json = requests.post(BASE_URL, json={})  # Sending an empty JSON object
        print(
            f"Status Code (Empty JSON): {response_empty_json.status_code}")  # Expected: 400 (due to missing required fields)
        try:
            pretty_print_json(response_empty_json.json())
        except json.JSONDecodeError:
            print(response_empty_json.text)

        print("\n--- 3b. Testing: POST Job - Incorrect: Non-JSON request body ---")
        # Test 3b: Non-JSON body (sending plain text)
        response_non_json = requests.post(BASE_URL, data="this is not json", headers={'Content-Type': 'text/plain'})
        print(
            f"Status Code (Non-JSON): {response_non_json.status_code}")  # Expected: 400 (for "Empty request or not JSON")
        try:
            pretty_print_json(response_non_json.json())
        except json.JSONDecodeError:
            print(response_non_json.text)

    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    print("-" * 30 + "\n")


def test_post_job_invalid_category_id():
    print(f"--- 4. Testing: POST Job - Incorrect: Invalid category_id ({NON_EXISTENT_CATEGORY_ID}) ---")
    payload = {
        "job": f"API Test Job - Invalid Category - {random.randint(1000, 9999)}",
        "team_leader_id": VALID_TEAM_LEADER_ID,
        "work_size": 5,
        "category_ids": [VALID_CATEGORY_IDS[0] if VALID_CATEGORY_IDS else 1, NON_EXISTENT_CATEGORY_ID]
        # Mix valid and invalid
    }
    try:
        response = requests.post(BASE_URL, json=payload)
        print(f"Status Code: {response.status_code}")  # Expected: 400 (if API checks category existence)
        print("Response JSON (or error message):")
        try:
            pretty_print_json(response.json())
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
    print("-" * 30 + "\n")


def test_get_all_jobs_after_post(created_job_id=None):
    print("--- 5. Testing: GET All Jobs (to verify addition) ---")
    try:
        response = requests.get(BASE_URL)
        print(f"Status Code: {response.status_code}")  # Expected: 200
        response.raise_for_status()
        all_jobs_data = response.json()
        pretty_print_json(all_jobs_data)

        if created_job_id and 'jobs' in all_jobs_data:
            found = any(job['id'] == created_job_id for job in all_jobs_data['jobs'])
            if found:
                print(f"\nSUCCESS: Newly created job with ID {created_job_id} was found in the list!")
            else:
                print(f"\nWARNING: Newly created job with ID {created_job_id} was NOT found in the list.")
        elif created_job_id:
            print(
                f"\nWARNING: Could not verify job ID {created_job_id} as 'jobs' key was not in response or list was empty.")


    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code from error: {e.response.status_code}")
            try:
                print(f"Response Content: {e.response.text}")
            except Exception:
                pass
    print("-" * 30 + "\n")


if __name__ == "__main__":
    print(f"Starting POST API tests for {BASE_URL}...\n")

    # Important: Replace VALID_TEAM_LEADER_ID and VALID_CATEGORY_IDS with actual,
    # existing IDs from your database for the tests to be meaningful.
    print(f"Using VALID_TEAM_LEADER_ID: {VALID_TEAM_LEADER_ID}")
    print(f"Using VALID_CATEGORY_IDS: {VALID_CATEGORY_IDS}\n")

    # 1. Correct POST request
    newly_created_job_id = test_post_job_correct()

    # 2. Incorrect: Missing required field
    test_post_job_missing_required_field()

    # 3. Incorrect: Empty or Non-JSON body
    test_post_job_empty_or_not_json()

    # 4. Incorrect: Invalid category ID
    test_post_job_invalid_category_id()

    # 5. GET all jobs to verify (if a job was created)
    test_get_all_jobs_after_post(newly_created_job_id)

    print("POST API tests finished.")
