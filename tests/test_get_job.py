import requests
import json

BASE_URL = "http://127.0.0.1:8080/api/jobs"


def pretty_print_json(data):
    print(json.dumps(data, indent=4, ensure_ascii=False))


def test_get_all_jobs():
    print("--- 1. Testing: Get All Jobs ---")
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        pretty_print_json(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            try:
                print(f"Response Content: {e.response.text}")
            except Exception:
                pass
    print("-" * 30 + "\n")
    return response.json() if response.ok and 'jobs' in response.json() else None


def test_get_one_job_correct(job_id_to_test):
    print(f"--- 2. Testing: Get One Job (Correct ID: {job_id_to_test}) ---")
    if job_id_to_test is None:
        print("Skipping correct single job test: No job ID available from 'get all jobs'.")
        print("-" * 30 + "\n")
        return

    try:
        response = requests.get(f"{BASE_URL}/{job_id_to_test}")
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        pretty_print_json(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            try:
                print(f"Response Content: {e.response.text}")
            except Exception:
                pass
    print("-" * 30 + "\n")


def test_get_one_job_incorrect_id(incorrect_id=99999):
    print(f"--- 3. Testing: Get One Job (Incorrect ID: {incorrect_id}) ---")
    try:
        response = requests.get(f"{BASE_URL}/{incorrect_id}")
        print(f"Status Code: {response.status_code}")
        print("Response JSON (or error message):")
        try:
            pretty_print_json(response.json())
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during request (should not happen if server is up): {e}")
    print("-" * 30 + "\n")


def test_get_one_job_string_id(string_id="abc"):
    print(f"--- 4. Testing: Get One Job (String ID: '{string_id}') ---")
    try:
        response = requests.get(f"{BASE_URL}/{string_id}")
        print(f"Status Code: {response.status_code}")
        print("Response text (Flask's default 404 page or your custom error):")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during request (should not happen if server is up): {e}")
    print("-" * 30 + "\n")


if __name__ == "__main__":
    print(f"Starting API tests for {BASE_URL}...\n")

    all_jobs_data = test_get_all_jobs()
    first_job_id = None
    if all_jobs_data and all_jobs_data.get('jobs') and len(all_jobs_data['jobs']) > 0:
        first_job_id = all_jobs_data['jobs'][0].get('id')
        print(f"Found first job ID for further testing: {first_job_id}\n")
    else:
        print("Could not retrieve a job ID from 'get all jobs'. Make sure there's at least one job in the DB.\n")

    if first_job_id:
        test_get_one_job_correct(first_job_id)
    else:
        print("No job ID from 'get all'. Trying with ID 1 for 'correct job' test (might fail if no job 1).")
        test_get_one_job_correct(1)

    test_get_one_job_incorrect_id()

    test_get_one_job_string_id()

    print("API tests finished.")
