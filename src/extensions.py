# src/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Cria as instâncias das extensões aqui, sem associá-las a um app.
db = SQLAlchemy()
login_manager = LoginManager()