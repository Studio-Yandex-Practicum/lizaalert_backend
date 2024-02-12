import pytest

from lizaalert.homeworks.models import Homework
from tests.factories.homeworks import HomeworkFactory


@pytest.mark.django_db(transaction=True)
class TestHomework:
    def test_creation_of_homework(self):
        """Тест, что модель Homework создается в БД."""
        homework = HomeworkFactory()
        obj = Homework.objects.get(id=homework.id)
        assert obj == homework
