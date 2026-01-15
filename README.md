# Сервер для учёта и контроля выдачи видеорегистраторов

Backend-сервер на Flask для мобильного приложения учёта и контроля выдачи видеорегистраторов в отделе АСКП ГУП "Мосгортранс".

## Технологии

- **Flask** - веб-фреймворк
- **SQLite** - база данных (простая файловая БД)
- **Flask-SQLAlchemy** - ORM для работы с БД
- **Flask-JWT-Extended** - аутентификация через JWT токены
- **Flask-CORS** - поддержка CORS для мобильного приложения

## Установка

1. Убедитесь, что у вас установлен Python 3.8+

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

### Локальный запуск

```bash
python app.py
```

Сервер запустится на `http://localhost:5000`

### Хостинг

Для хостинга на сервере (например, используя gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Или через WSGI-сервер (например, для PythonAnywhere, Heroku, etc.):

```python
# wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

## API Endpoints

### Аутентификация

- `POST /api/auth/login` - Авторизация пользователя
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
  
- `GET /api/auth/me` - Получение информации о текущем пользователе (требуется JWT токен)
  
- `POST /api/auth/register` - Создание нового пользователя (только для администраторов)

### Видеорегистраторы (UC2, UC3)

- `GET /api/video-recorders` - Получение списка всех видеорегистраторов
- `GET /api/video-recorders/<id>` - Получение информации о видеорегистраторе
- `POST /api/video-recorders` - Добавление видеорегистратора (только админ)
- `PUT /api/video-recorders/<id>` - Редактирование видеорегистратора (только админ)
- `DELETE /api/video-recorders/<id>` - Удаление видеорегистратора (только админ)

### Сотрудники (UC4)

- `GET /api/employees` - Получение списка сотрудников
- `GET /api/employees/<id>` - Получение информации о сотруднике
- `POST /api/employees` - Добавление сотрудника (только админ)
- `PUT /api/employees/<id>` - Редактирование сотрудника (только админ)
- `DELETE /api/employees/<id>` - Удаление сотрудника (только админ)
- `POST /api/employees/<id>/photo` - Загрузка фотографии сотрудника (только админ)
- `GET /api/employees/<id>/photo` - Получение фотографии сотрудника

### Выдача и возврат (UC5, UC6, UC7)

- `POST /api/issues/issue` - Выдача видеорегистратора сотруднику
  ```json
  {
    "video_recorder_id": 1,
    "employee_id": 1
  }
  ```
  
- `POST /api/issues/return` - Возврат видеорегистратора
  ```json
  {
    "video_recorder_id": 1,
    "employee_id": 1
  }
  ```
  
- `GET /api/issues/history` - История выдачи и возврата
  - Параметры запроса (опционально): `video_recorder_id`, `employee_id`
  
- `GET /api/issues/active` - Список активных выдач

## Использование JWT токенов

После успешной авторизации, сервер вернёт JWT токен:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

Используйте этот токен в заголовке запросов:
```
Authorization: Bearer <your_token>
```

## Роли пользователей

- **admin** - Администратор с полными правами (может управлять пользователями, видеорегистраторами, сотрудниками)
- **operator** - Оператор (может выдавать и принимать видеорегистраторы, просматривать данные)

## База данных

База данных SQLite создаётся автоматически при первом запуске в файле `video_recorders.db`.

При первом запуске автоматически создаются роли:
- admin
- operator

Для создания первого администратора используйте скрипт или API после создания пользователя вручную через Python:

```python
from app import app, db
from models import User, Role
from werkzeug.security import generate_password_hash

with app.app_context():
    admin_role = Role.query.filter_by(name='admin').first()
    admin_user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        last_name='Админ',
        first_name='Админ',
        role_id=admin_role.id
    )
    db.session.add(admin_user)
    db.session.commit()
```

## Структура проекта

```
.
├── app.py                  # Главный файл приложения
├── models.py               # Модели базы данных
├── routes/                 # Маршруты API
│   ├── __init__.py
│   ├── auth.py            # Аутентификация
│   ├── video_recorders.py # Управление видеорегистраторами
│   ├── employees.py       # Управление сотрудниками
│   └── issues.py          # Выдача и возврат
├── uploads/                # Загруженные файлы (фотографии)
├── video_recorders.db      # База данных SQLite (создаётся автоматически)
├── requirements.txt        # Зависимости Python
└── README.md              # Документация
```

## Переменные окружения

Для продакшн-окружения установите:

- `SECRET_KEY` - секретный ключ Flask
- `JWT_SECRET_KEY` - секретный ключ для JWT
- `DATABASE_URL` - URL базы данных (по умолчанию SQLite)

Пример для `.env` файла (используйте python-dotenv для загрузки):

```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///video_recorders.db
```

## Заметки о хостинге

- SQLite подходит для небольших проектов и простого хостинга
- Для продакшн-окружения рекомендуется использовать PostgreSQL или MySQL
- Убедитесь, что папка `uploads` доступна для записи
- Настройте CORS для вашего домена мобильного приложения
