from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import VideoRecorder, User, VideoRecorderIssue, VideoRecorderReturn
from database import db

video_recorders_bp = Blueprint('video_recorders', __name__)

@video_recorders_bp.route('', methods=['GET'])
@jwt_required()
def get_video_recorders():
    """UC2: Просмотр списка видеорегистраторов и их статуса"""
    video_recorders = VideoRecorder.query.all()
    return jsonify([vr.to_dict() for vr in video_recorders]), 200

@video_recorders_bp.route('', methods=['POST'])
@jwt_required()
def create_video_recorder():
    """UC3: Добавление видеорегистратора"""
    current_user_id = int(get_jwt_identity())  # Преобразуем строку в int
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может добавлять)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('number'):
        return jsonify({'error': 'Требуется номер видеорегистратора'}), 400
    
    if VideoRecorder.query.filter_by(number=data['number']).first():
        return jsonify({'error': 'Видеорегистратор с таким номером уже существует'}), 400
    
    new_video_recorder = VideoRecorder(
        number=data['number'],
        status=data.get('status', 'available')
    )
    
    db.session.add(new_video_recorder)
    db.session.commit()
    
    return jsonify({'message': 'Видеорегистратор добавлен', 'video_recorder': new_video_recorder.to_dict()}), 201

@video_recorders_bp.route('/<int:video_recorder_id>', methods=['GET'])
@jwt_required()
def get_video_recorder(video_recorder_id):
    """Получение информации о конкретном видеорегистраторе"""
    video_recorder = VideoRecorder.query.get(video_recorder_id)
    
    if not video_recorder:
        return jsonify({'error': 'Видеорегистратор не найден'}), 404
    
    return jsonify(video_recorder.to_dict()), 200

@video_recorders_bp.route('/<int:video_recorder_id>', methods=['PUT'])
@jwt_required()
def update_video_recorder(video_recorder_id):
    """UC3: Редактирование видеорегистратора"""
    current_user_id = int(get_jwt_identity())  # Преобразуем строку в int
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может редактировать)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    video_recorder = VideoRecorder.query.get(video_recorder_id)
    
    if not video_recorder:
        return jsonify({'error': 'Видеорегистратор не найден'}), 404
    
    data = request.get_json()
    
    if 'number' in data:
        # Проверка уникальности номера
        existing = VideoRecorder.query.filter_by(number=data['number']).first()
        if existing and existing.id != video_recorder_id:
            return jsonify({'error': 'Видеорегистратор с таким номером уже существует'}), 400
        video_recorder.number = data['number']
    
    if 'status' in data:
        if data['status'] not in ['available', 'issued']:
            return jsonify({'error': 'Недопустимый статус'}), 400
        video_recorder.status = data['status']
    
    db.session.commit()
    
    return jsonify({'message': 'Видеорегистратор обновлён', 'video_recorder': video_recorder.to_dict()}), 200

@video_recorders_bp.route('/<int:video_recorder_id>', methods=['DELETE'])
@jwt_required()
def delete_video_recorder(video_recorder_id):
    """UC3: Удаление видеорегистратора"""
    current_user_id = int(get_jwt_identity())  # Преобразуем строку в int
    current_user = User.query.get(current_user_id)
    
    # Проверка прав (только администратор может удалять)
    if not current_user or current_user.role.name != 'admin':
        return jsonify({'error': 'Недостаточно прав'}), 403
    
    video_recorder = VideoRecorder.query.get(video_recorder_id)
    
    if not video_recorder:
        return jsonify({'error': 'Видеорегистратор не найден'}), 404
    
    # Проверка, что видеорегистратор не выдан
    if video_recorder.status == 'issued':
        return jsonify({'error': 'Нельзя удалить видеорегистратор, который сейчас выдан'}), 400
    
    try:
        # Удаляем видеорегистратор, история выдач/возвратов сохранится
        # (внешние ключи установятся в NULL благодаря ondelete='SET NULL')
        db.session.delete(video_recorder)
        db.session.commit()
        return jsonify({'message': 'Видеорегистратор удалён'}), 200
    except Exception as e:
        db.session.rollback()
        # Если БД не поддерживает SET NULL, обновляем внешние ключи вручную
        from models import VideoRecorderIssue, VideoRecorderReturn
        VideoRecorderIssue.query.filter_by(video_recorder_id=video_recorder_id).update({'video_recorder_id': None})
        VideoRecorderReturn.query.filter_by(video_recorder_id=video_recorder_id).update({'video_recorder_id': None})
        db.session.delete(video_recorder)
        db.session.commit()
        return jsonify({'message': 'Видеорегистратор удалён, история сохранена'}), 200
