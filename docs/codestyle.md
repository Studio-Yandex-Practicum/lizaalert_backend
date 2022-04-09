## Общие рекомендации к коду проекта

### Про код
- Используем [black style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
- Длина строки — 119 символов;
- Для сортировки импортов используем пакет [isort](https://pycqa.github.io/isort/), следим чтобы не было неиспользуемых;
- Отступы — 4 пробела;
- Консистентность: одинаковые кавычки, одинаковые методы решения одинаковых проблем;
- Комментарии к функциям оформлены в виде Docstrings в соответствии с Docstring Conventions: 
начинаются с большой буквы, заканчиваются точкой и содержат описание того, что делает функция; 
- Логические блоки кода выделены пустыми строками;
- Используется [Guard Block](https://refactoring.guru/ru/replace-nested-conditional-with-guard-clauses);
- Следим, чтобы в репозиторий не попадали системные и временные файлы (__pycache__, .vscode, и т.д.);

- Где возможно используем кортежи вместо списков ([обзор различий](https://www.educative.io/edpresso/tuples-vs-list-in-python))

Вместо такого:
```python
filters = ["test"]
```
Делаем так:
```python
filters = ("test",)
```

- f-строки предпочтительнее остальных способов форматирования строк

Так плохо:
```python
def ugly_one(self):
    return "{smth} - {here}".format({"smth": self.smth, "here": self.here})
```
Так хорошо:
```python
def nice_one(self):
    return f"{self.smth} - {self.here}"
```

- В f-строках только подстановка переменных

Так плохо:
```python
f"some_result: {UsingSomeClass.and_ofcourse_method('with', a, self.bunch, of, USEFUL_PARAMS)}"
```
Так хорошо:
```python
# делаем полезное и понятное
some_result = ...
f"some_result: {some_result}"
```

- Переменные названы в соответствии с их смыслом, по-английски, нет однобуквенных названий и транслита;
- Используем [Type Hints](https://docs.python.org/3/library/typing.html);

### Про Django
- В urls.py в конце роутов стоит слеш /;
- Для URL применяются соответствующие [path converters](https://docs.djangoproject.com/en/4.0/topics/http/urls/#path-converters);
- Для всех ссылок используется reverse();
- Отсутствие закомментированного кода и стандартных комментариев Django (# Create your views here. и другие);
- Отсутствие любых пустых файлов *.py в модулях Django (urls.py, views.py и других);
- Соблюдается [официальный код-стайл Django](https://docs.djangoproject.com/en/3.2/internals/contributing/writing-code/coding-style/) (Если он не противоречит PEP8, настройкам линтеров и форматеров кода);

### Про тесты

- Все ключевые участки кода покрыты тестами: каждый ответ каждого эндпоинта API и важная бизнес-логика;
- У тестов есть понятное описание, что именно проверяется внутри. Используйте [pep257](https://peps.python.org/pep-0257/).
