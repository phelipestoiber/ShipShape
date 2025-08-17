# src/models/user.py

from flask_login import UserMixin
from src.extensions import db
from sqlalchemy import Date

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    segment = db.Column(db.String(100), nullable=False)

    # Relação: Um usuário pode ter várias embarcações
    # 'back_populates' cria uma referência de volta do Vessel para o User
    vessels = db.relationship('Vessel', back_populates='owner')