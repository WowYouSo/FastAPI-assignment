import pytest


def test_user_journey(client):
    registration_data = {"username": "scenario_user", "password": "secure_password"}
    
    register_response = client.post("/register", json=registration_data)
    assert register_response.status_code == 200
    
    login_response = client.post("/login", data={"username": registration_data["username"], "password": registration_data["password"]})
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    authorized_headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Новая задача из сценария",
        "description": "Это задача создана в рамках сценарного теста",
        "status": "в работе",
        "priority": 2
    }
    
    create_task_response = client.post("/tasks", json=task_data, headers=authorized_headers)
    assert create_task_response.status_code == 200
    task_id = create_task_response.json()["id"]
    
    get_tasks_response = client.get("/tasks", headers=authorized_headers)
    assert get_tasks_response.status_code == 200
    
    tasks = get_tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    
    updated_task_data = {
        "title": "Обновленная задача",
        "description": "Это обновленное описание",
        "status": "завершено",
        "priority": 1
    }
    
    update_response = client.put(f"/tasks/{task_id}", json=updated_task_data, headers=authorized_headers)
    assert update_response.status_code == 200
    
    updated_task = update_response.json()
    assert updated_task["title"] == updated_task_data["title"]
    assert updated_task["status"] == updated_task_data["status"]
    
    delete_response = client.delete(f"/tasks/{task_id}", headers=authorized_headers)
    assert delete_response.status_code == 200
    
    get_deleted_task = client.get(f"/tasks/{task_id}", headers=authorized_headers)
    assert get_deleted_task.status_code == 404
    
    get_tasks_after_delete = client.get("/tasks", headers=authorized_headers)
    assert get_tasks_after_delete.status_code == 200
    assert len(get_tasks_after_delete.json()) == 0


def test_multiple_tasks_management(client):
    user_data = {"username": "multi_task_user", "password": "test_password"}
    
    client.post("/register", json=user_data)
    login_response = client.post("/login", data=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    tasks_to_create = [
        {"title": "Высокий приоритет", "description": "Важная задача", "priority": 1, "status": "в ожидании"},
        {"title": "Средний приоритет", "description": "Задача со средней важностью", "priority": 2, "status": "в работе"},
        {"title": "Низкий приоритет", "description": "Не очень важная задача", "priority": 3, "status": "в ожидании"}
    ]
    
    task_ids = []
    for task_data in tasks_to_create:
        response = client.post("/tasks", json=task_data, headers=headers)
        assert response.status_code == 200
        task_ids.append(response.json()["id"])
    
    top_tasks_response = client.get("/tasks?top_n=2", headers=headers)
    assert top_tasks_response.status_code == 200
    
    top_tasks = top_tasks_response.json()
    assert len(top_tasks) == 2
    assert top_tasks[0]["priority"] == 1
    assert top_tasks[1]["priority"] == 2

    search_response = client.get("/tasks?search=важная", headers=headers)
    assert search_response.status_code == 200
    
    search_results = search_response.json()
    assert len(search_results) == 1
    
    for task_id in task_ids:
        task_data = client.get(f"/tasks/{task_id}", headers=headers).json()
        task_data["status"] = "завершено"
        update_response = client.put(f"/tasks/{task_id}", json=task_data, headers=headers)
        assert update_response.status_code == 200
    
    all_tasks_response = client.get("/tasks", headers=headers)
    all_tasks = all_tasks_response.json()
    
    for task in all_tasks:
        assert task["status"] == "завершено"
    
    for task_id in task_ids:
        delete_response = client.delete(f"/tasks/{task_id}", headers=headers)
        assert delete_response.status_code == 200
    
    final_tasks_response = client.get("/tasks", headers=headers)
    assert len(final_tasks_response.json()) == 0


def test_concurrent_access(client):
    user1_data = {
        "username": "user1",
        "password": "password1"
    }
    client.post("/register", json=user1_data)
    user1_login = client.post("/login", data=user1_data)
    user1_token = user1_login.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    user2_data = {
        "username": "user2",
        "password": "password2"
    }
    client.post("/register", json=user2_data)
    user2_login = client.post("/login", data=user2_data)
    user2_token = user2_login.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    user1_task = {
        "title": "Задача пользователя 1",
        "description": "Это задача создана пользователем 1",
        "priority": 1
    }
    user1_create_response = client.post("/tasks", json=user1_task, headers=user1_headers)
    assert user1_create_response.status_code == 200
    user1_task_id = user1_create_response.json()["id"]
    
    user2_task = {
        "title": "Задача пользователя 2",
        "description": "Это задача создана пользователем 2",
        "priority": 2
    }
    user2_create_response = client.post("/tasks", json=user2_task, headers=user2_headers)
    assert user2_create_response.status_code == 200
    user2_task_id = user2_create_response.json()["id"]
    
    user1_tasks = client.get("/tasks", headers=user1_headers).json()
    user2_tasks = client.get("/tasks", headers=user2_headers).json()
    
    assert len(user1_tasks) == 2
    assert len(user2_tasks) == 2
    
    user1_get_own_task = client.get(f"/tasks/{user1_task_id}", headers=user1_headers)
    assert user1_get_own_task.status_code == 200
    
    user2_get_own_task = client.get(f"/tasks/{user2_task_id}", headers=user2_headers)
    assert user2_get_own_task.status_code == 200
    
    user1_update_user2_task = client.put(
        f"/tasks/{user2_task_id}", 
        json={"title": "Обновлено пользователем 1", "description": "Обновление чужой задачи", "priority": 3, "status": "в работе"},
        headers=user1_headers
    )
    assert user1_update_user2_task.status_code == 200
    
    client.delete(f"/tasks/{user1_task_id}", headers=user1_headers)
    client.delete(f"/tasks/{user2_task_id}", headers=user2_headers)