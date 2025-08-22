from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange, InputRequired

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

    calado_min = FloatField('Calado Mínimo (m)', validators=[InputRequired("Campo obrigatório."), NumberRange(min=0, message="O valor deve ser maior ou igual a 0.")])
    calado_max = FloatField('Calado Máximo (m)', validators=[InputRequired("Campo obrigatório."), NumberRange(min=0, message="O valor deve ser maior ou igual a 0.")])

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
        
        # --- Garante que calado_max > calado_min ---
        if self.calado_max.data is not None and self.calado_min.data is not None:
            if self.calado_max.data <= self.calado_min.data:
                # Adiciona uma mensagem de erro especificamente ao campo calado_max
                self.calado_max.errors.append('O calado máximo deve ser maior que o calado mínimo.')
                return False # Interrompe a validação

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