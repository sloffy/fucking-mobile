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
    print("Проверка ролей...")
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("Создание роли 'admin'...")
        admin_role = Role(name='admin', description='Администратор с полными правами')
        db.session.add(admin_role)
        db.session.commit()
        print("✓ Роль 'admin' создана")
    else:
        print("✓ Роль 'admin' уже существует")
    
    operator_role = Role.query.filter_by(name='operator').first()
    if not operator_role:
        print("Создание роли 'operator'...")
        operator_role = Role(name='operator', description='Оператор, может выдавать и принимать видеорегистраторы')
        db.session.add(operator_role)
        db.session.commit()
        print("✓ Роль 'operator' создана")
    else:
        print("✓ Роль 'operator' уже существует")
    
    # Обновляем admin_role после возможного создания
    admin_role = Role.query.filter_by(name='admin').first()
    
    # Проверка, существует ли администратор
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("\nПользователь 'admin' уже существует!")
        print(f"ID: {admin_user.id}, Роль: {admin_user.role.name if admin_user.role else 'не указана'}")
        response = input("Хотите изменить пароль? (y/n): ")
        if response.lower() == 'y':
            new_password = input("Введите новый пароль: ")
            admin_user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print("✓ Пароль обновлён!")
    else:
        print("\nСоздание пользователя администратора...")
        username = input("Введите логин (по умолчанию 'admin'): ") or 'admin'
        password = input("Введите пароль: ")
        if not password:
            print("Ошибка: пароль не может быть пустым!")
            exit(1)
        last_name = input("Введите фамилию (по умолчанию 'Админ'): ") or 'Админ'
        first_name = input("Введите имя (по умолчанию 'Админ'): ") or 'Админ'
        middle_name = input("Введите отчество (необязательно, Enter для пропуска): ").strip() or None
        
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
        print(f"\n✓ Пользователь '{username}' успешно создан!")
        print(f"  ID: {admin_user.id}")
        print(f"  Роль: {admin_role.name}")
    
    # Вывод списка всех пользователей
    print("\n" + "="*50)
    print("Список всех пользователей в системе:")
    all_users = User.query.all()
    if all_users:
        for user in all_users:
            role_name = user.role.name if user.role else 'не указана'
            print(f"  - {user.username} (ID: {user.id}, Роль: {role_name})")
    else:
        print("  Пользователей нет")
    
    print("="*50)
