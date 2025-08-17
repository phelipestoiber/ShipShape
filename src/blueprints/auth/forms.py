# src/blueprints/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from src.models import User

class RegistrationForm(FlaskForm):
    """
    Formulário de registro de usuário.
    Define os campos do formulário e suas regras de validação.
    """
    # Campo de nome
    first_name = StringField('Nome',
                             validators=[DataRequired("Este campo é obrigatório.")])
    
    # Campo de Sobrenome
    last_name = StringField('Sobrenome',
                            validators=[DataRequired("Este campo é obrigatório.")])
    
    # Campo de Data de Nascimento
    birth_date = DateField('Data de Nascimento',
                           validators=[DataRequired("Este campo é obrigatório.")])
    
    # Campo de E-mail
    email = StringField('E-mail', 
                        validators=[DataRequired("Este campo é obrigatório."), 
                                    Email("Formato de e-mail inválido.")])
    
    # Campo de Nome de Usuário
    username = StringField('Nome de Usuário', 
                           validators=[DataRequired("Este campo é obrigatório."), 
                                       Length(min=4, max=25, message="O nome de usuário deve ter entre 4 e 25 caracteres.")])
    
    # Campo de Senha
    password = PasswordField('Senha', 
                             validators=[DataRequired("Este campo é obrigatório."), 
                                         Length(min=6, message="A senha deve ter no mínimo 6 caracteres.")])
    
    # Campo de Confirmação de Senha
    confirm_password = PasswordField('Confirmar Senha', 
                                     validators=[DataRequired("Este campo é obrigatório."), 
                                                 EqualTo('password', message="As senhas devem ser iguais.")])
    
    # Campos adicionais do seu modelo User
    job = StringField('Função', validators=[DataRequired("Este campo é obrigatório.")])
    company = StringField('Empresa', validators=[DataRequired("Este campo é obrigatório.")])
    segment = StringField('Segmento da Empresa', validators=[DataRequired("Este campo é obrigatório.")])

    # Botão de Envio
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        """Verifica se o e-mail já existe no banco de dados."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            # Se encontrou um usuário, levanta um erro de validação.
            raise ValidationError('Este e-mail já está cadastrado. Por favor, escolha outro.')

    # 4. ADICIONE ESTE OUTRO NOVO MÉTODO
    def validate_username(self, username):
        """Verifica se o nome de usuário já existe no banco de dados."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            # Se encontrou um usuário, levanta um erro de validação.
            raise ValidationError('Este nome de usuário já está em uso. Por favor, escolha outro.')


class LoginForm(FlaskForm):
    """
    Formulário de login de usuário.
    """
    email = StringField('E-mail',
                        validators=[DataRequired("Este campo é obrigatório."), 
                                    Email("Formato de e-mail inválido.")])
    
    password = PasswordField('Senha', 
                             validators=[DataRequired("Este campo é obrigatório.")])

    remember_me = BooleanField('Lembrar-me')

    submit = SubmitField('Entrar')