import pytest
from fastapi import status
from datetime import datetime
import time

@pytest.fixture
def task_data():
    return {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи",
        "status": "в ожидании",
        "priority": 1
    }

def test_create_task(authorized_client, task_data):
    response = authorized_client.post("/tasks", json=task_data)

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert data["priority"] == task_data["priority"]
    assert "id" in data
    assert "creation_time" in data
    assert "details" not in data


def test_create_task_unauthorized(client, task_data):
    response = client.post("/tasks", json=task_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_tasks_empty(authorized_client):
    response = authorized_client.get("/tasks")
    
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks(authorized_client, task_data):
    created = authorized_client.post("/tasks", json=task_data).json()
    response = authorized_client.get("/tasks")

    assert response.status_code == 200
    
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == created["id"]
    assert tasks[0]["title"] == task_data["title"]
    assert tasks[0]["description"] == task_data["description"]
    assert tasks[0]["status"] == task_data["status"]
    assert tasks[0]["priority"] == task_data["priority"]


def test_get_task_by_id(authorized_client, task_data):
    created = authorized_client.post("/tasks", json=task_data).json()
    task_id = created["id"]
    
    response = authorized_client.get(f"/tasks/{task_id}")
    
    assert response.status_code == 200
    
    task = response.json()
    assert task["id"] == task_id
    assert task["title"] == task_data["title"]
    assert task["description"] == task_data["description"]
    assert task["status"] == task_data["status"]
    assert task["priority"] == task_data["priority"]


def test_get_nonexistent_task(authorized_client):
    response = authorized_client.get("/tasks/999999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Задачи с данным id не существует, эхб"


def test_update_task(authorized_client, task_data):
    created = authorized_client.post("/tasks", json=task_data).json()
    task_id = created["id"]
    
    updated_data = {
        "title": "Обновленная задача",
        "description": "Обновленное описание",
        "status": "в работе",
        "priority": 2
    }
    
    response = authorized_client.put(f"/tasks/{task_id}", json=updated_data)
    assert response.status_code == 200

    updated = response.json()
    assert updated["id"] == task_id
    assert updated["title"] == updated_data["title"]
    assert updated["description"] == updated_data["description"]
    assert updated["status"] == updated_data["status"]
    assert updated["priority"] == updated_data["priority"]

def test_update_task_unauthorized(client, task_data):
    response = client.put("/tasks/1", json=task_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_nonexistent_task(authorized_client, task_data):
    response = authorized_client.put("/tasks/999999", json=task_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Задачи с данным id не существует, эхб"


def test_delete_task(authorized_client, task_data):
    created = authorized_client.post("/tasks", json=task_data).json()
    task_id = created["id"]
    response = authorized_client.delete(f"/tasks/{task_id}")
    
    assert response.status_code == 200
    assert f"Задача с id {task_id} удалена" in response.json()["message"]
    get_response = authorized_client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_task_unauthorized(client):
    response = client.delete("/tasks/1")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_delete_nonexistent_task(authorized_client):
    response = authorized_client.delete("/tasks/999999")
    
    assert response.status_code == 404
    assert "Задачи с данным id не существует" in response.json()["detail"]


def test_sort_tasks_by_title(authorized_client):
    tasks_to_create = [
        {"title": "C задача", "description": "Описание", "status": "в ожидании", "priority": 1},
        {"title": "A задача", "description": "Описание", "status": "в ожидании", "priority": 1},
        {"title": "B задача", "description": "Описание", "status": "в ожидании", "priority": 1}
    ]
    
    for task in tasks_to_create:
        authorized_client.post("/tasks", json=task)
    
    response = authorized_client.get("/tasks?sort_by=title&order=asc")
    assert response.status_code == 200
    
    tasks = response.json()
    titles = [task["title"] for task in tasks]
    
    assert titles == ["A задача", "B задача", "C задача"]
    response = authorized_client.get("/tasks?sort_by=title&order=desc")
    assert response.status_code == 200
    tasks = response.json()
    titles = [task["title"] for task in tasks]
    assert titles == ["C задача", "B задача", "A задача"]


def test_sort_tasks_by_status(authorized_client):
    tasks_to_create = [
        {"title": "Задача 1", "description": "Описание", "status": "завершено", "priority": 1},
        {"title": "Задача 2", "description": "Описание", "status": "в ожидании", "priority": 1},
        {"title": "Задача 3", "description": "Описание", "status": "в работе", "priority": 1}
    ]
    
    for task in tasks_to_create:
        authorized_client.post("/tasks", json=task)
    response = authorized_client.get("/tasks?sort_by=status&order=asc")
    assert response.status_code == 200
    
    tasks = response.json()
    statuses = [task["status"] for task in tasks]
    
    assert statuses == ["в ожидании", "в работе", "завершено"]

def test_sort_tasks_by_creation_time(authorized_client, task_data):
    for i in range(3):
        task_data["title"] = f"Задача {i+1}"
        authorized_client.post("/tasks", json=task_data)
        time.sleep(1.5)
    
    response = authorized_client.get("/tasks?sort_by=creation_time&order=asc")
    assert response.status_code == 200
    
    tasks = response.json()
    titles = [task["title"] for task in tasks]
    assert titles == ["Задача 1", "Задача 2", "Задача 3"]
    response = authorized_client.get("/tasks?sort_by=creation_time&order=desc")
    assert response.status_code == 200
    tasks = response.json()
    titles = [task["title"] for task in tasks]
    assert titles == ["Задача 3", "Задача 2", "Задача 1"]


def test_invalid_sort_criteria(authorized_client):
    response = authorized_client.get("/tasks?sort_by=invalid_field")
    
    assert response.status_code == 400
    assert "Недопустимый критерий сортировки" in response.json()["detail"]


def test_top_n_tasks_by_priority(authorized_client):
    tasks_to_create = [
        {"title": "Задача с высоким приоритетом", "description": "Описание", "status": "в ожидании", "priority": 1},
        {"title": "Задача с низким приоритетом", "description": "Описание", "status": "в ожидании", "priority": 3},
        {"title": "Задача со средним приоритетом", "description": "Описание", "status": "в ожидании", "priority": 2}
    ]
    
    for task in tasks_to_create:
        authorized_client.post("/tasks", json=task)
    
    response = authorized_client.get("/tasks?top_n=2")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    
    assert tasks[0]["priority"] == 1
    assert tasks[1]["priority"] == 2


def test_invalid_top_n(authorized_client):
    response = authorized_client.get("/tasks?top_n=0")
    
    assert response.status_code == 400
    assert "top_n должен быть положительным числом" in response.json()["detail"]


def test_search_tasks(authorized_client):
    tasks_to_create = [
        {"title": "Встреча с клиентом", "description": "Обсудить проект", "status": "в ожидании", "priority": 1},
        {"title": "Разработка", "description": "Создать новый проект", "status": "в ожидании", "priority": 1},
        {"title": "Проект дизайна", "description": "Создать дизайн для клиента", "status": "в ожидании", "priority": 1}
    ]
    
    for task in tasks_to_create:
        authorized_client.post("/tasks", json=task)
    response = authorized_client.get("/tasks?search=проект")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    response = authorized_client.get("/tasks?search=клиент")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    response = authorized_client.get("/tasks?search=несуществующий")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 0


def test_combined_filter(authorized_client):
    tasks_to_create = [
        {"title": "Проект A", "description": "Важное задание", "status": "в ожидании", "priority": 1},
        {"title": "Задание B", "description": "Проект для клиента", "status": "в работе", "priority": 2},
        {"title": "Проект C", "description": "Обычное задание", "status": "завершено", "priority": 3}
    ]
    
    for task in tasks_to_create:
        authorized_client.post("/tasks", json=task)
    response = authorized_client.get("/tasks?search=Проект&sort_by=status&order=asc")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    statuses = [task["status"] for task in tasks]
    assert statuses == ["в ожидании", "в работе", "завершено"]
