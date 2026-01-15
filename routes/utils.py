"""
Утилиты для работы с JWT и пользователями
"""
from flask_jwt_extended import get_jwt_identity
from models import User

def get_current_user():
    """
    Получает текущего пользователя из JWT токена
    Возвращает User объект или None, если пользователь не найден
    """
    try:
        current_user_id = int(get_jwt_identity())
        return User.query.get(current_user_id)
    except (ValueError, TypeError):
        return None
