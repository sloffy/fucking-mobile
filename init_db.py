"""
Скрипт для инициализации базы данных
Создаёт таблицы и роли (admin, operator)
Запустите: python init_db.py
"""
from app import app
from database import db
from models import Role

with app.app_context():
    print("Инициализация базы данных...")
    
    # Создание всех таблиц
    db.create_all()
    print("✓ Таблицы созданы")
    
    # Создание ролей, если их нет
    if Role.query.count() == 0:
        print("Создание ролей...")
        admin_role = Role(name='admin', description='Администратор с полными правами')
        operator_role = Role(name='operator', description='Оператор, может выдавать и принимать видеорегистраторы')
        db.session.add(admin_role)
        db.session.add(operator_role)
        db.session.commit()
        print("✓ Роли созданы: admin, operator")
    else:
        roles = Role.query.all()
        print(f"✓ Роли уже существуют: {', '.join([r.name for r in roles])}")
    
    print("\nБаза данных инициализирована!")
    print("Теперь вы можете создать администратора с помощью: python create_admin.py")
