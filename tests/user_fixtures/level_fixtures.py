import pytest

levels = [
    {"id": 1, "name": "Новичок", "slug": "novice"},
    {"id": 2, "name": "Бывалый", "slug": "experienced"},
    {"id": 3, "name": "Профессионал", "slug": "professional"},
]


@pytest.fixture()
def create_levels():
    from users.models import Level

    [Level.objects.create(name=level["name"], description="test") for level in levels]


def return_levels_data():
    from users.models import Level

    out = [{"id": o.id, "name": o.name, "slug": o.get_name_display()} for o in Level.objects.all()]
    return out
