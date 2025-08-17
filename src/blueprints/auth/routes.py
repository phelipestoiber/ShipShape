# src/blueprints/auth/routes.py

from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash # Para criptografar a senha

from .forms import RegistrationForm, LoginForm # Importa nossa classe de formulário
from src.models import User
from src.extensions import db

from flask_login import login_user, logout_user, login_required

# 1. A linha mais importante: Cria a variável 'auth_bp' como um Blueprint.
#    É essa variável que o __init__.py está procurando.
auth_bp = Blueprint(
    'auth', __name__,
    template_folder='templates'
)

# 2. Agora, criamos as rotas usando '@auth_bp.route(...)'
@auth_bp.route('/')
def index():
    """
    Rota principal da aplicação. Redireciona para a página de login.
    """
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Exibe e processa o formulário de login.
    """
    form = LoginForm()
    if form.validate_on_submit():
        # 1. Busca o usuário no banco de dados pelo e-mail fornecido.
        user = User.query.filter_by(email=form.email.data).first()

        # 2. Verifica se o usuário existe E se a senha fornecida corresponde à senha
        # criptografada que está salva no banco de dados.
        if user and check_password_hash(user.password, form.password.data):
            
            # 3. Se as credenciais estiverem corretas, cria a sessão do usuário.
            login_user(user, remember=form.remember_me.data)
            
            # flash('Login realizado com sucesso!', 'success')
            
            # Redireciona para uma página protegida (vamos criá-la a seguir).
            return redirect(url_for('user.profile'))
        
        # 4. Se as credenciais estiverem incorretas, exibe uma mensagem de erro.
        flash('E-mail ou senha inválidos. Por favor, tente novamente.', 'danger')

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Exibe e processa o formulário de registro.
    """
    form = RegistrationForm() # Cria uma instância do formulário

    # A mágica acontece aqui:
    # Se o formulário foi submetido (POST) e passou em todas as validações...
    if form.validate_on_submit():
        
        # ANTES DE SALVAR: NUNCA SALVE SENHAS EM TEXTO PURO!
        # Usamos generate_password_hash para criar uma versão criptografada da senha.
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Cria um novo objeto User com os dados do formulário
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_date=form.birth_date.data,
            email=form.email.data,
            username=form.username.data,
            job=form.job.data,
            company=form.company.data,
            segment=form.segment.data,
            password=hashed_password
        )

        # Adiciona o novo usuário à sessão do banco de dados
        db.session.add(new_user)
        # Confirma a transação, salvando o usuário no banco de dados
        db.session.commit()

        # Envia uma mensagem de sucesso para o usuário
        flash('Sua conta foi criada com sucesso! Você já pode fazer login.', 'success')

        # Redireciona o usuário para a página de login
        return redirect(url_for('auth.login'))
    
    elif request.method == 'POST':
        # Se a requisição for POST mas a validação falhou, pegamos os erros.
        for field, errors in form.errors.items():
            for error in errors:
                # Para cada erro encontrado no formulário, criamos um pop-up de erro.
                flash(error, category='error')

    # Se a requisição for GET, ou se o formulário tiver erros de validação,
    # apenas renderiza o template com o formulário.
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    # 1. A FUNÇÃO ESSENCIAL
    logout_user() 

    # 2. FEEDBACK PARA O USUÁRIO
    flash('Você foi desconectado com sucesso!', 'success') 

    # 3. REDIRECIONAMENTO
    return redirect(url_for('auth.login'))