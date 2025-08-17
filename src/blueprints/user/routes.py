from flask import Blueprint, render_template
from flask_login import login_required, current_user

# 1. Define o novo blueprint
# O primeiro argumento 'user' será usado no url_for (ex: 'user.profile')
user_bp = Blueprint(
    'user', 
    __name__,
    template_folder='templates',
    url_prefix='/user'  # Adiciona /user na frente de todas as rotas deste blueprint
)

# 2. Cria a rota da página de perfil
@user_bp.route('/profile')
@login_required  # Protege a rota, exigindo que o usuário esteja logado
def profile():
    """
    Exibe a página de perfil do usuário logado.
    """
    # O objeto 'current_user' já está disponível globalmente nos templates
    # graças ao Flask-Login, então não precisamos passá-lo aqui.
    return render_template('profile.html')