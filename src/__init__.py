# src/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .extensions import db, login_manager
from .models import User


def create_app():
    """Constrói o core da aplicação."""
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Associa as instâncias importadas com a aplicação Flask
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Redireciona usuários não logados para a rota de login

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        """
        Esta função é chamada pelo Flask-Login em cada requisição
        para carregar o usuário logado a partir do seu ID, que está
        armazenado na sessão.
        
        Args:
            user_id (str): O ID do usuário a ser carregado.

        Returns:
            User | None: O objeto do usuário se encontrado, caso contrário None.
        """
        # user_id vem como string, então convertemos para inteiro para buscar no BD.
        return User.query.get(int(user_id))
    
    with app.app_context():
        # Importa os blueprints
        from .blueprints.auth import routes as auth_routes
        from .blueprints.hidrostatica import routes as hidrostatica_routes
        from .blueprints.cruzadas import routes as cruzadas_routes
        from .blueprints.user import routes as user_routes
        from .blueprints.vessel import routes as vessel_routes

        # Registra os blueprints na aplicação
        app.register_blueprint(auth_routes.auth_bp)
        app.register_blueprint(hidrostatica_routes.hidrostatica_bp, url_prefix='/hidrostatica')
        app.register_blueprint(cruzadas_routes.cruzadas_bp, url_prefix='/cruzadas')
        app.register_blueprint(user_routes.user_bp)
        app.register_blueprint(vessel_routes.vessel_bp)

        # Cria as tabelas do banco de dados se não existirem
        db.create_all()

        return app