import pytest

statuses = [
  {
    "id": 1,
    "name": "Активный",
    "slug": "active"
  },
  {
    "id": 2,
    "name": "Вы записаны",
    "slug": "booked"
  },
  {
    "id": 3,
    "name": "Пройден",
    "slug": "finished"
  },
  {
    "id": 4,
    "name": "Не активный",
    "slug": "inactive"
  }
]

class TestCourseStatus:

    def test_coursestatus_list_not_found(self, user_client):
        response = user_client.get(f'/api/v1/users/course_statuses/')

        assert response.status_code != 404

    def test_coursestatus_list_anonimous(self, client):
        response = client.get(f'/api/v1/users/course_statuses/')
        assert response.status_code == 401

    def test_coursestatus_list(self, user_client, create_statuses):
        response = user_client.get(f'/api/v1/users/course_statuses/')

        assert response.status_code == 200
        assert response.json() == statuses