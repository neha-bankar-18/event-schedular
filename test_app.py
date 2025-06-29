import pytest
from app import app, events, save_events

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_create_event(client):
    response = client.post('/events', json={
        "title": "Test Event",
        "description": "Unit Test Desc",
        "start_time": "2025-12-31 10:00",
        "end_time": "2025-12-31 11:00",
        "recurrence": "none",
        "email_notify": False
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['event']['title'] == "Test Event"

def test_get_all_events(client):
    response = client.get('/events')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_search_event(client):
    client.post('/events', json={
        "title": "Meeting Alpha",
        "description": "Project A",
        "start_time": "2025-12-30 09:00",
        "end_time": "2025-12-30 10:00"
    })
    response = client.get('/events/search?q=Alpha')
    assert response.status_code == 200
    assert any("Alpha" in e['title'] for e in response.get_json())

def test_update_event(client):
    response = client.put('/events/1', json={
        "title": "Updated Title"
    })
    assert response.status_code in [200, 404]  # 404 if event 1 doesn't exist
    if response.status_code == 200:
        assert response.get_json()['event']['title'] == "Updated Title"

def test_delete_event(client):
    response = client.delete('/events/9999')  # Assume high ID unlikely to exist
    assert response.status_code == 404 or response.status_code == 200

def test_upcoming_reminders(client):
    response = client.get('/upcoming_reminders')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
