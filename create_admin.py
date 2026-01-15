"""
Скрипт для создания администратора в базе данных
Запустите: python create_admin.py
"""
from app import app
from database import db
from models import User, Role
from werkzeug.security import generate_password_hash

with app.app_context():
    # Создание базы данных, если её нет
    db.create_all()
    
    # Создание ролей, если их нет
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Администратор с полными правами')
        db.session.add(admin_role)
        db.session.commit()
    
    operator_role = Role.query.filter_by(name='operator').first()
    if not operator_role:
        operator_role = Role(name='operator', description='Оператор, может выдавать и принимать видеорегистраторы')
        db.session.add(operator_role)
        db.session.commit()
    
    # Проверка, существует ли администратор
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("Пользователь 'admin' уже существует!")
        response = input("Хотите изменить пароль? (y/n): ")
        if response.lower() == 'y':
            new_password = input("Введите новый пароль: ")
            admin_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print("Пароль обновлён!")
    else:
        print("Создание пользователя администратора...")
        username = input("Введите логин (по умолчанию 'admin'): ") or 'admin'
        password = input("Введите пароль: ")
        last_name = input("Введите фамилию: ") or 'Админ'
        first_name = input("Введите имя: ") or 'Админ'
        middle_name = input("Введите отчество (необязательно): ") or None
        
        admin_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            role_id=admin_role.id
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print(f"Пользователь '{username}' успешно создан!")
