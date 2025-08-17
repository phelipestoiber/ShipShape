# src/blueprints/cruzadas/routes.py

from flask import Blueprint, render_template
from flask_login import login_required # Garante que o usuário deve estar logado

# 1. Cria o Blueprint
cruzadas_bp = Blueprint(
    'cruzadas', __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. Define a rota principal deste blueprint
@cruzadas_bp.route('/')
@login_required # Protege a rota
def index():
    """
    Exibe a página de cálculo de curvas cruzadas.
    """
    # Como você mencionou que os templates serão os mesmos, podemos reutilizá-los!
    # Apenas passamos dados diferentes para o mesmo template.
    page_title = "Cálculo de Curvas Cruzadas"
    return render_template('calculos.html', title=page_title)