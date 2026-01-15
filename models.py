from database import db
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    users = db.relationship('User', backref='role', lazy=True)

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Text)
    employee_number = db.Column(db.String(6), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    photo = db.relationship('EmployeePhoto', backref='employee', uselist=False, lazy=True)
    issues = db.relationship('VideoRecorderIssue', backref='employee', lazy=True)
    returns = db.relationship('VideoRecorderReturn', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'position': self.position,
            'employee_number': self.employee_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'photo_url': f'/api/employees/{self.id}/photo' if self.photo else None
        }

class VideoRecorder(db.Model):
    __tablename__ = 'video_recorders'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='available', nullable=False)  # available/issued
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    issues = db.relationship('VideoRecorderIssue', backref='video_recorder', lazy=True)
    returns = db.relationship('VideoRecorderReturn', backref='video_recorder', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    middle_name = db.Column(db.String(80))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    
    issues = db.relationship('VideoRecorderIssue', foreign_keys='VideoRecorderIssue.issued_by_user_id', backref='issued_by_user', lazy=True)
    returns = db.relationship('VideoRecorderReturn', foreign_keys='VideoRecorderReturn.returned_by_user_id', backref='returned_by_user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None
        }

class EmployeePhoto(db.Model):
    __tablename__ = 'employee_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), unique=True, nullable=False)

class VideoRecorderIssue(db.Model):
    __tablename__ = 'video_recorder_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    video_recorder_id = db.Column(db.Integer, db.ForeignKey('video_recorders.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    issued_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='issued', nullable=False)  # issued/returned
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_recorder_id': self.video_recorder_id,
            'video_recorder_number': self.video_recorder.number if self.video_recorder else None,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'issued_by_user_id': self.issued_by_user_id,
            'issued_by_user_name': f"{self.issued_by_user.first_name} {self.issued_by_user.last_name}" if self.issued_by_user else None,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'status': self.status
        }

class VideoRecorderReturn(db.Model):
    __tablename__ = 'video_recorder_returns'
    
    id = db.Column(db.Integer, primary_key=True)
    video_recorder_id = db.Column(db.Integer, db.ForeignKey('video_recorders.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    returned_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_recorder_id': self.video_recorder_id,
            'video_recorder_number': self.video_recorder.number if self.video_recorder else None,
            'employee_id': self.employee_id,
            'employee_name': self.employee.full_name if self.employee else None,
            'returned_by_user_id': self.returned_by_user_id,
            'returned_by_user_name': f"{self.returned_by_user.first_name} {self.returned_by_user.last_name}" if self.returned_by_user else None,
            'return_date': self.return_date.isoformat() if self.return_date else None
        }
