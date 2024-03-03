# Blogicum
<img width="860" alt="image" src="https://github.com/evgeniazagorodnykh/django-blogicum/assets/129388336/1e913332-0217-4ac2-b376-6ac16680e778">

## Описание
Социальная сеть, где пользователи могут отслеживать посты любимых авторов и оставлять свои комментарии, а также делиться своими постами и добавлять к ним картинки.

## Разверните проект на своём компьютере:
На своём компьютере в директории с проектами создайте папку для проекта YaNews.
Склонируйте проект Blogicum из репозитория: 
```
git clone …
```
Создайте виртуальное окружение 
```
python -m venv venv
```
Запустите виртуальное окружение и установите зависимости из файла requirements.txt: 
```
pip install -r requirements.txt
```
Миграции уже созданы, выполните их: 
```
python manage.py migrate.
```
Cоздайте суперпользователя: 
```
python manage.py createsuperuser.
```
Запустите проект:
```
python manage.py runserver
```
