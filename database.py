from flask_sqlalchemy import SQLAlchemy

# Инициализация db без привязки к app
# app будет передан позже через init_app
db = SQLAlchemy()
