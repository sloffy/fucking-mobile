from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Role
from database import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """UC1: Авторизация пользователя в системе"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Требуется логин и пароль'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Неверный логин или пароль'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """Создание нового пользователя (требуется авторизация)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может создавать пользователей)
    if not current_user or (current_user.role.name != 'admin'):
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    
    required_fields = ['username', 'password', 'last_name', 'first_name', 'role_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Пользователь с таким логином уже существует'}), 400
    
    role = Role.query.get(data['role_id'])
    if not role:
        return jsonify({'error': 'Роль не найдена'}), 404
    
    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        last_name=data['last_name'],
        first_name=data['first_name'],
        middle_name=data.get('middle_name'),
        role_id=data['role_id']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Пользователь создан', 'user': new_user.to_dict()}), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Получение информации о текущем пользователе"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404
    
    return jsonify(user.to_dict()), 200
