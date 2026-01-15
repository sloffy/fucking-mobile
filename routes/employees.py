from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import Employee, EmployeePhoto, User
from database import db
import os

employees_bp = Blueprint('employees', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@employees_bp.route('', methods=['GET'])
@jwt_required()
def get_employees():
    """UC4: Просмотр списка сотрудников"""
    employees = Employee.query.all()
    return jsonify([emp.to_dict() for emp in employees]), 200

@employees_bp.route('', methods=['POST'])
@jwt_required()
def create_employee():
    """UC4: Добавление сотрудника"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может добавлять)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    
    required_fields = ['full_name', 'employee_number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    if Employee.query.filter_by(employee_number=data['employee_number']).first():
        return jsonify({'error': 'Сотрудник с таким табельным номером уже существует'}), 400
    
    new_employee = Employee(
        full_name=data['full_name'],
        position=data.get('position'),
        employee_number=data['employee_number']
    )
    
    db.session.add(new_employee)
    db.session.commit()
    
    return jsonify({'message': 'Сотрудник добавлен', 'employee': new_employee.to_dict()}), 201

@employees_bp.route('/<int:employee_id>', methods=['GET'])
@jwt_required()
def get_employee(employee_id):
    """Получение информации о конкретном сотруднике"""
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    return jsonify(employee.to_dict()), 200

@employees_bp.route('/<int:employee_id>', methods=['PUT'])
@jwt_required()
def update_employee(employee_id):
    """UC4: Редактирование сотрудника"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может редактировать)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    data = request.get_json()
    
    if 'full_name' in data:
        employee.full_name = data['full_name']
    
    if 'position' in data:
        employee.position = data['position']
    
    if 'employee_number' in data:
        # Проверка уникальности табельного номера
        existing = Employee.query.filter_by(employee_number=data['employee_number']).first()
        if existing and existing.id != employee_id:
            return jsonify({'error': 'Сотрудник с таким табельным номером уже существует'}), 400
        employee.employee_number = data['employee_number']
    
    db.session.commit()
    
    return jsonify({'message': 'Сотрудник обновлён', 'employee': employee.to_dict()}), 200

@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    """UC4: Удаление сотрудника"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может удалять)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    # Удаление фотографии, если есть
    if employee.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employee_photos', employee.photo.filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
        db.session.delete(employee.photo)
    
    db.session.delete(employee)
    db.session.commit()
    
    return jsonify({'message': 'Сотрудник удалён'}), 200

@employees_bp.route('/<int:employee_id>/photo', methods=['POST'])
@jwt_required()
def upload_employee_photo(employee_id):
    """Загрузка фотографии сотрудника"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может загружать фотографии)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    if 'photo' not in request.files:
        return jsonify({'error': 'Файл не предоставлен'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Недопустимый тип файла'}), 400
    
    filename = secure_filename(f"employee_{employee_id}_{file.filename}")
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employee_photos', filename)
    file.save(filepath)
    
    # Удаление старой фотографии, если есть
    if employee.photo:
        old_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employee_photos', employee.photo.filename)
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
        employee.photo.filename = filename
        employee.photo.mime_type = file.content_type
    else:
        new_photo = EmployeePhoto(
            filename=filename,
            mime_type=file.content_type,
            employee_id=employee_id
        )
        db.session.add(new_photo)
    
    db.session.commit()
    
    return jsonify({'message': 'Фотография загружена'}), 200

@employees_bp.route('/<int:employee_id>/photo', methods=['GET'])
@jwt_required()
def get_employee_photo(employee_id):
    """Получение фотографии сотрудника"""
    employee = Employee.query.get(employee_id)
    
    if not employee or not employee.photo:
        return jsonify({'error': 'Фотография не найдена'}), 404
    
    photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'employee_photos', employee.photo.filename)
    
    if not os.path.exists(photo_path):
        return jsonify({'error': 'Файл фотографии не найден'}), 404
    
    return send_file(photo_path, mimetype=employee.photo.mime_type)
