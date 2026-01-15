from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import VideoRecorderIssue, VideoRecorderReturn, VideoRecorder, Employee, User
from database import db

issues_bp = Blueprint('issues', __name__)

@issues_bp.route('/issue', methods=['POST'])
@jwt_required()
def issue_video_recorder():
    """UC5: Инициализация выдачи видеорегистратора сотруднику"""
    current_user_id = int(get_jwt_identity())  # Преобразуем строку в int
    
    data = request.get_json()
    
    required_fields = ['video_recorder_id', 'employee_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    video_recorder = VideoRecorder.query.get(data['video_recorder_id'])
    if not video_recorder:
        return jsonify({'error': 'Видеорегистратор не найден'}), 404
    
    if video_recorder.status == 'issued':
        return jsonify({'error': 'Видеорегистратор уже выдан'}), 400
    
    employee = Employee.query.get(data['employee_id'])
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404

    # Ограничение: одному сотруднику может быть выдан только один видеорегистратор одновременно
    existing_active_issue_for_employee = VideoRecorderIssue.query.filter_by(
        employee_id=data['employee_id'],
        status='issued'
    ).first()
    if existing_active_issue_for_employee:
        return jsonify({
            'error': 'Сотруднику уже выдан видеорегистратор. Сначала оформите возврат.',
            'active_issue': existing_active_issue_for_employee.to_dict()
        }), 400
    
    new_issue = VideoRecorderIssue(
        video_recorder_id=data['video_recorder_id'],
        employee_id=data['employee_id'],
        issued_by_user_id=current_user_id,
        status='issued'
    )
    
    video_recorder.status = 'issued'
    
    db.session.add(new_issue)
    db.session.commit()
    
    return jsonify({'message': 'Видеорегистратор выдан', 'issue': new_issue.to_dict()}), 201

@issues_bp.route('/return', methods=['POST'])
@jwt_required()
def return_video_recorder():
    """UC6: Инициализация возврата видеорегистратора"""
    current_user_id = int(get_jwt_identity())  # Преобразуем строку в int
    
    data = request.get_json()
    
    required_fields = ['video_recorder_id', 'employee_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Отсутствуют обязательные поля'}), 400
    
    video_recorder = VideoRecorder.query.get(data['video_recorder_id'])
    if not video_recorder:
        return jsonify({'error': 'Видеорегистратор не найден'}), 404
    
    if video_recorder.status == 'available':
        return jsonify({'error': 'Видеорегистратор не был выдан'}), 400
    
    employee = Employee.query.get(data['employee_id'])
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
    
    # Проверка, что видеорегистратор был выдан этому сотруднику
    active_issue = VideoRecorderIssue.query.filter_by(
        video_recorder_id=data['video_recorder_id'],
        employee_id=data['employee_id'],
        status='issued'
    ).first()
    
    if not active_issue:
        return jsonify({'error': 'Этот видеорегистратор не был выдан данному сотруднику'}), 400
    
    # Создание записи о возврате
    new_return = VideoRecorderReturn(
        video_recorder_id=data['video_recorder_id'],
        employee_id=data['employee_id'],
        returned_by_user_id=current_user_id
    )
    
    # Обновление статуса видеорегистратора и записи о выдаче
    video_recorder.status = 'available'
    active_issue.status = 'returned'
    
    db.session.add(new_return)
    db.session.commit()
    
    return jsonify({'message': 'Видеорегистратор возвращён', 'return': new_return.to_dict()}), 201

@issues_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """UC7: Просмотр истории выдачи и возврата видеорегистраторов"""
    video_recorder_id = request.args.get('video_recorder_id', type=int)
    employee_id = request.args.get('employee_id', type=int)
    
    issues = VideoRecorderIssue.query
    returns = VideoRecorderReturn.query
    
    # Используем явную проверку на None, чтобы корректно обрабатывать id = 0
    if video_recorder_id is not None:
        issues = issues.filter_by(video_recorder_id=video_recorder_id)
        returns = returns.filter_by(video_recorder_id=video_recorder_id)
    
    if employee_id is not None:
        issues = issues.filter_by(employee_id=employee_id)
        returns = returns.filter_by(employee_id=employee_id)
    
    issues_list = [issue.to_dict() for issue in issues.all()]
    returns_list = [ret.to_dict() for ret in returns.all()]
    
    return jsonify({
        'issues': issues_list,
        'returns': returns_list
    }), 200

@issues_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_issues():
    """Получение списка активных выдач (видеорегистраторы, которые сейчас выданы)"""
    active_issues = VideoRecorderIssue.query.filter_by(status='issued').all()
    return jsonify([issue.to_dict() for issue in active_issues]), 200
