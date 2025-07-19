# Блогикум

Блогикум - сервис, который позволяет зарегистрироваться, создать, отредактировать или удалить собственный пост, прокомментировать пост другого автора и подписаться на него.

## Технологии:
- python 3.9
- Django 3.2
- Pillow 9.3

Автор [SprogisArina](https://github.com/SprogisArina)

## Как локально запустить проект:

Клонировать репозиторий:

```
git clone git@github.com:SprogisArina/django_sprint4.git
cd django_sprint4
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/Scripts/activate
```

Обновить pip и установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Создать суперпользователя:

```
python manage.py createsuperuser
```

Запустить проект:

```
python manage.py runserver
```
