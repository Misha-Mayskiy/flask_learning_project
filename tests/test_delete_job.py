import requests

BASE_URL = "http://127.0.0.1:8080/api"


def test_delete_job_success():
    """
    Тест успешного удаления существующей работы.
    """
    # 1. Сначала создадим работу, которую будем удалять.
    print("\n--- test_delete_job_success ---")
    job_data_to_create = {
        "job": "Test Job for Deletion",
        "team_leader_id": 1,
        "work_size": 10,
        "collaborators": "1,2",
        "is_finished": False,
        "category_ids": []
    }
    print(f"POST {BASE_URL}/jobs with data: {job_data_to_create}")
    response_create = requests.post(f"{BASE_URL}/jobs", json=job_data_to_create)
    assert response_create.status_code == 201, \
        (f"Failed to create job for deletion test. Status: {response_create.status_code},"
         f" Response: {response_create.text}")
    created_job_id = response_create.json()['job']['id']
    print(f"Job created successfully with ID: {created_job_id}")

    # 2. Удаляем созданную работу
    print(f"DELETE {BASE_URL}/jobs/{created_job_id}")
    response_delete = requests.delete(f"{BASE_URL}/jobs/{created_job_id}")
    assert response_delete.status_code == 204, \
        f"Delete failed. Status: {response_delete.status_code}, Response: {response_delete.text}"
    assert not response_delete.content, "Delete response should have no content for 204"
    print(f"Job {created_job_id} deleted successfully.")

    # 3. Проверяем, что работа действительно удалена (попытка получить ее должна вернуть 404)
    print(f"GET {BASE_URL}/jobs/{created_job_id} (expecting 404)")
    response_get_deleted = requests.get(f"{BASE_URL}/jobs/{created_job_id}")
    assert response_get_deleted.status_code == 404, \
        f"Job {created_job_id} was not actually deleted. GET returned {response_get_deleted.status_code}"
    print(f"Confirmed job {created_job_id} is deleted (GET returned 404).")

    # 4. Дополнительно: получаем список всех работ и убеждаемся, что удаленной там нет
    print(f"GET {BASE_URL}/jobs (verifying list)")
    response_get_all = requests.get(f"{BASE_URL}/jobs")
    if response_get_all.status_code == 200:
        jobs_list = response_get_all.json().get('jobs', [])
        for job in jobs_list:
            assert job['id'] != created_job_id, f"Deleted job {created_job_id} still found in the list of all jobs!"
        print("Deleted job not found in the list of all jobs.")
    elif response_get_all.status_code == 404:
        print("List of jobs is now empty (or was empty before), which is fine after deletion.")
    else:
        assert False, \
            (f"Failed to get all jobs to verify deletion. Status: {response_get_all.status_code},"
             f" Response: {response_get_all.text}")
    print("--- test_delete_job_success PASSED ---")


def test_delete_non_existent_job():
    """
    Тест удаления несуществующей работы (ожидаем 404).
    """
    print("\n--- test_delete_non_existent_job ---")
    non_existent_job_id = 99999
    print(f"DELETE {BASE_URL}/jobs/{non_existent_job_id}")
    response = requests.delete(f"{BASE_URL}/jobs/{non_existent_job_id}")
    assert response.status_code == 404, \
        f"Expected 404 for non-existent job, got {response.status_code}. Response: {response.text}"
    assert 'error' in response.json(), "Error message not found in JSON response for non-existent job deletion"
    print(f"Received 404 for non-existent job ID {non_existent_job_id} as expected.")
    print("--- test_delete_non_existent_job PASSED ---")


def test_delete_job_with_invalid_id_type():
    """
    Тест удаления работы с некорректным типом ID (например, строкой).
    Flask обычно сам обрабатывает это и возвращает 404, так как маршрут не совпадает.
    """
    print("\n--- test_delete_job_with_invalid_id_type ---")
    invalid_job_id = "abc"
    print(f"DELETE {BASE_URL}/jobs/{invalid_job_id}")
    response = requests.delete(f"{BASE_URL}/jobs/{invalid_job_id}")
    # Ожидаем 404, так как Flask не найдет маршрут для <string:job_id>
    assert response.status_code == 404, f"Expected 404 for invalid ID type, got {response.status_code}. Response: {response.text}"
    print(f"Received 404 for invalid job ID type '{invalid_job_id}' as expected.")
    print("--- test_delete_job_with_invalid_id_type PASSED ---")


if __name__ == "__main__":
    print("Running Jobs API DELETE tests...")
    test_delete_job_success()
    test_delete_non_existent_job()
    test_delete_job_with_invalid_id_type()
    print("\nAll tests finished.")
