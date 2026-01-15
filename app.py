from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from datetime import timedelta

app = Flask(__name__)

# Конфигурация
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Абсолютный путь к instance и БД
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)
DB_PATH = os.path.join(INSTANCE_DIR, 'video_recorders.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

# Создание папки для загрузок, если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'employee_photos'), exist_ok=True)

# Инициализация расширений
from database import db
db.init_app(app)
cors = CORS(app)
jwt = JWTManager(app)

# Импорт моделей (после инициализации db)
from models import Role, Employee, VideoRecorder, User, EmployeePhoto, VideoRecorderIssue, VideoRecorderReturn

# Импорт маршрутов
from routes.auth import auth_bp
from routes.video_recorders import video_recorders_bp
from routes.employees import employees_bp
from routes.issues import issues_bp

# Регистрация blueprint'ов
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(video_recorders_bp, url_prefix='/api/video-recorders')
app.register_blueprint(employees_bp, url_prefix='/api/employees')
app.register_blueprint(issues_bp, url_prefix='/api/issues')

@app.route('/')
def index():
    return {'message': 'Video Recorders Management API', 'version': '1.0'}

@app.route('/api/health')
def health():
    return {'status': 'ok'}

def init_database():
    """Инициализация базы данных: создание таблиц и ролей"""
    try:
        with app.app_context():
            db.create_all()
            # Создание ролей по умолчанию, если их нет
            if Role.query.count() == 0:
                admin_role = Role(name='admin', description='Администратор с полными правами')
                operator_role = Role(name='operator', description='Оператор, может выдавать и принимать видеорегистраторы')
                db.session.add(admin_role)
                db.session.add(operator_role)
                db.session.commit()
                print("Роли созданы: admin, operator")
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")

# Инициализация БД при импорте (для WSGI на PythonAnywhere)
# На локальной машине это также сработает
init_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
