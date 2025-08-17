from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional, ValidationError

class HydrostaticsCalculationForm(FlaskForm):
    """Formulário para executar um cálculo hidrostático."""

    # Este campo será populado dinamicamente na rota
    vessel = SelectField('Selecione a Embarcação', coerce=int, validators=[DataRequired()])

    # Radio buttons para escolher o método de cálculo
    calc_method = RadioField(
        'Método de Definição dos Calados',
        choices=[
            ('numero', 'Por número de calados'),
            ('incremento', 'Por incremento de calados em metros'),
            ('manual', 'Lista manual de calados em metros')
        ],
        default='numero',
        validators=[DataRequired()]
    )

    # Campos de entrada para cada método
    num_calados = IntegerField("Número de Calados", validators=[Optional()])
    inc_calados = FloatField("Incremento (m)", validators=[Optional()])
    lista_calados = StringField("Lista (separada por ;)", validators=[Optional()])

    # Campos de parâmetros
    metodo_interp = SelectField(
        'Método de Interpolação',
        choices=[('linear', 'Linear'), ('pchip', 'PCHIP')],
        default='linear',
        validators=[DataRequired()]
    )
    densidade = FloatField('Densidade (t/m³)', default=1.025, validators=[DataRequired()])

    submit = SubmitField('Executar Cálculo')

    # Validação personalizada para os campos de calado
    def validate(self, extra_validators=None):
        # Primeiro, roda as validações padrão
        if not super(HydrostaticsCalculationForm, self).validate(extra_validators):
            return False

        # Agora, a lógica condicional
        method = self.calc_method.data
        if method == 'numero':
            if not self.num_calados.data:
                self.num_calados.errors.append('Este campo é obrigatório para o método selecionado.')
                return False
        elif method == 'incremento':
            if not self.inc_calados.data:
                self.inc_calados.errors.append('Este campo é obrigatório para o método selecionado.')
                return False
        elif method == 'manual':
            if not self.lista_calados.data:
                self.lista_calados.errors.append('Este campo é obrigatório para o método selecionado.')
                return False
        
        return True