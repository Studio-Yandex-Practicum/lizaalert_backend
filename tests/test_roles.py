import pytest

from users.models import UserRole, User


class TestRoleAPI:

    @pytest.mark.django_db(transaction=True)
    def test_user_roles_url(self, client, user):
        response = client.get(f"/api/v1/users/{user.id}/roles/")

        code = 200
        assert response.status_code == code, ("Эндпоинт /api/v1/users/{user.id}/roles/ недоступен.")

    @pytest.mark.django_db(transaction=True)
    def test_get_user_roles(self, client, user, user_admin_teacher_role):
        response = client.get(f"/api/v1/users/{user.id}/roles/")

        test_data = response.json()
        assert type(test_data) == list, ("Ответ должен содержать тип данных list.")

        assert len(test_data) == UserRole.objects.filter(user=user.id).count()

        assert "id" in test_data[0], ("В ответе не содержится поле id.")

        assert "role" in test_data[0], ("В ответе не содержится поле role.")

        assert "user" in test_data[0], ("В ответе не содержится поле user.")

    @pytest.mark.django_db(transaction=True)
    def test_create_user_roles(self, client, user, role_main_admin, role_teacher):
        user_role_data_1 = {"role": role_teacher}
        user_role_admin_data = {"role": role_main_admin}
        user_role_incorrect_data = {"role", "incorrect role"}

        client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_data_1)
        user_roles = UserRole.objects.filter(user=user)
        assert user_roles.count() == 1, ("Проверьте, что метод POST добавляет роль для пользователя.")

        assert user_roles[0].role == user_role_data_1["role"], ("Роль для пользователя создана неверно.")

        try:
            client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_data_1)
        except Exception:
            pass
        assert UserRole.objects.filter(user=user).count() == 1, ("Роли у пользователя должны быть уникальны.")

        client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_admin_data)
        assert user_roles.count() == 2, ("У пользователя может быть несколько ролей.")

        try:
            client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_incorrect_data)
        except Exception:
            pass
        assert UserRole.objects.filter(user=user).count() == 2, (
            "Пользователю могут быть добавлены только роли из списка."
        )

    @pytest.mark.django_db(transaction=True)
    def test_delete_user_roles(self, client, user, user_admin_teacher_role):
        response = client.get(f"/api/v1/users/{user.id}/roles/")
        role_id = response.json()[0]["id"]
        client.delete(f"/api/v1/users/{user.id}/roles/{role_id}/")

        assert UserRole.objects.count() == 1, ("Проверьте, что метод DELETE удаляет роль у пользователя.")

        assert not UserRole.objects.filter(user=user, id=role_id).exists(), (
            "Проверьте, что метод DELETE удаляет нужную роль у пользователя."
        )

    @pytest.mark.django_db(transaction=True)
    def test_admin_user_roles(self, client, user, role_main_admin, role_teacher):
        user_role_data_1 = {"role": role_teacher}
        user_role_admin_data = {"role": role_main_admin}

        client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_data_1)
        assert not User.objects.get(id=user.id).is_superuser, (
            "Пользователь, не имеющий роль main admin, не должен иметь прав суперпользователя."
        )

        client.post(f"/api/v1/users/{user.id}/roles/", data=user_role_admin_data)
        assert User.objects.get(id=user.id).is_superuser, (
            "Пользователь, имеющий роль main admin, должен иметь права суперпользователя."
        )

        response = client.get(f"/api/v1/users/{user.id}/roles/")
        role_id = [role['id'] for role in response.json() if role["role"] == role_main_admin][0]
        client.delete(f"/api/v1/users/{user.id}/roles/{role_id}/")
        assert not User.objects.get(id=user.id).is_superuser, (
            "Пользователь, не имеющий роль main admin, не должен иметь прав суперпользователя."
        )
