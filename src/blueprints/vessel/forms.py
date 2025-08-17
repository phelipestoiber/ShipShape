from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SelectField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, NumberRange

VESSEL_TYPES = [
    ('', '-- Selecione o Tipo --'),
    ('Alvarenga', 'Alvarenga'), ('Anfíbia', 'Anfíbia'), ('Apoio a Mergulho', 'Apoio a Mergulho'),
    ('Apoio a Manobra', 'Apoio a Manobra'), ('Apoio a ROV', 'Apoio a ROV'), ('Balsa', 'Balsa'),
    ('Barcaça', 'Barcaça'), ('Bote', 'Bote'), ('Cábrea', 'Cábrea'), ('Caiaque', 'Caiaque'),
    ('Canoa', 'Canoa'), ('Carga de Alta Velocidade (HSC)', 'Carga de Alta Velocidade (HSC)'),
    ('Chata', 'Chata'), ('Cisterna', 'Cisterna'), ('Dique', 'Dique'), ('Draga', 'Draga'),
    ('Empurrador', 'Empurrador'), ('Escuna', 'Escuna'), ('Estimulador de Poços', 'Estimulador de Poços'),
    ('Ferry Boat', 'Ferry Boat'), ('Flotel', 'Flotel'), ('Flutuante', 'Flutuante'),
    ('FPSO', 'FPSO (Floating Production Storage and Offloading)'),
    ('FSO', 'FSO (Floating Storage and Offloading)'), ('Gaseiro', 'Gaseiro'),
    ('Graneleiro', 'Graneleiro'), ('Guindaste', 'Guindaste'), ('Hidroavião', 'Hidroavião'),
    ('Hovercraft', 'Hovercraft'), ('Iate', 'Iate'), ('Jangada', 'Jangada'),
    ('Lançadora de Linhas (PLV)', 'Lançadora de Linhas (PLV)'), ('Lancha', 'Lancha'),
    ('Moto Aquática (Jet Ski)', 'Moto Aquática (Jet Ski)'), ('Multicasco', 'Multicasco'),
    ('Navio de Carga Geral', 'Navio de Carga Geral'), ('Navio de Passageiros', 'Navio de Passageiros'),
    ('Navio Tanque', 'Navio Tanque'), ('Nuclear', 'Nuclear'), ('Paquete', 'Paquete'),
    ('Passageiros de Alta Velocidade (HSC)', 'Passageiros de Alta Velocidade (HSC)'),
    ('Pesca', 'Pesca'), ('Petroleiro', 'Petroleiro'), ('Plataforma', 'Plataforma'),
    ('Porta-Contentores', 'Porta-Contentores'), ('Quebra-Gelo', 'Quebra-Gelo'),
    ('Rebocador', 'Rebocador'), ('Recolhedor de Óleo (OSRV)', 'Recolhedor de Óleo (OSRV)'),
    ('Rolo (Roll-on/Roll-off)', 'Rolo (Roll-on/Roll-off)'), ('Saveiro', 'Saveiro'),
    ('Sonda', 'Sonda'), ('Supridor (Supply)', 'Supridor (Supply)'),
    ('Tanque (transporte de granéis líquidos)', 'Tanque (transporte de granéis líquidos)'),
    ('Traineira', 'Traineira'), ('Transporte de Gado', 'Transporte de Gado'),
    ('Transporte de Veículos (PCC/PCTC)', 'Transporte de Veículos (PCC/PCTC)'),
    ('Veleiro', 'Veleiro'), ('Well Stimulation Vessel (WSV)', 'Well Stimulation Vessel (WSV)'),
    ('Outras', 'Outras')
]

# Lista de atividades/serviços baseada na NORMAM
VESSEL_SERVICES = [
    ('', '-- Selecione o Serviço --'),
    ('Apoio a Mergulho', 'Apoio a Mergulho'),
    ('Apoio Marítimo', 'Apoio Marítimo'),
    ('Apoio Portuário', 'Apoio Portuário'),
    ('Ciência e Pesquisa', 'Ciência e Pesquisa'),
    ('Esporte e/ou Recreio', 'Esporte e/ou Recreio'),
    ('Pesca', 'Pesca'),
    ('Serviço Público', 'Serviço Público'),
    ('Transporte de Carga', 'Transporte de Carga'),
    ('Transporte de Passageiros', 'Transporte de Passageiros'),
    ('Dragagem', 'Dragagem'),
    ('Turismo', 'Turismo'),
    ('Outro', 'Outro')
]

class VesselForm(FlaskForm):
    """Formulário para cadastrar uma nova embarcação com validação atualizada."""
    
    # --- Dados de Identificação ---
    name = StringField('Nome da Embarcação', validators=[DataRequired()])
    imo = IntegerField('Número IMO', validators=[Optional(), NumberRange(min=0, max=9999999, message="IMO deve ser um número de até 7 dígitos.")])
    n_inscricao = StringField('Número de Inscrição', validators=[DataRequired()])
    indicativo = StringField('Indicativo de Chamada', validators=[Optional()])

    # --- Dados de Classificação ---
    tipo = SelectField(
        'Tipo da Embarcação',
        choices=VESSEL_TYPES,
        validators=[DataRequired("Selecione um tipo.")]
    )
    area_navegacao = SelectField(
        'Área de Navegação',
        choices=[
            ('', '-- Selecione --'), 
            ('Mar Aberto', 'Mar Aberto'),
            ('Interior_1', 'Navegação Interior Área 1'),
            ('Interior_2', 'Navegação Interior Área 2')
        ],
        validators=[DataRequired("Selecione uma área.")]
    )
    propulsada = SelectField(
        'Propulsada?',
        choices=[('True', 'Sim'), ('False', 'Não')],
        validators=[DataRequired("Este campo é obrigatório.")]
    )
    servico_1 = SelectField('Atividade/Serviço Principal', choices=VESSEL_SERVICES, validators=[DataRequired("Selecione ao menos um serviço.")])
    servico_2 = SelectField('Atividade/Serviço 2', choices=VESSEL_SERVICES, validators=[Optional()])
    servico_3 = SelectField('Atividade/Serviço 3', choices=VESSEL_SERVICES, validators=[Optional()])
    servico_4 = SelectField('Atividade/Serviço 4', choices=VESSEL_SERVICES, validators=[Optional()])
    
    # --- Dados Construtivos ---
    construction_year = IntegerField('Ano de Construção', validators=[DataRequired(), NumberRange(min=1800, max=2100)])
    hull_material = StringField('Material do Casco', validators=[DataRequired()])
    port_of_registry = StringField('Porto de Inscrição', validators=[DataRequired()])
    construction_location = StringField('Local de Construção', validators=[DataRequired()])
    builder_shipyard = StringField('Estaleiro Construtor', validators=[DataRequired()])

    # --- Dimensões Principais ---
    lpp = FloatField('LPP (m)', validators=[DataRequired(), NumberRange(min=0)])
    boca = FloatField('Boca (m)', validators=[DataRequired(), NumberRange(min=0)])
    pontal = FloatField('Pontal (m)', validators=[DataRequired(), NumberRange(min=0)])
    
    # --- Capacidades (NÃO OBRIGATÓRIOS) ---
    crew_number = IntegerField('Nº de Tripulantes', validators=[Optional(), NumberRange(min=0)])
    passenger_number = IntegerField('Nº de Passageiros', validators=[Optional(), NumberRange(min=0)])
    extra_roll_number = IntegerField('Nº de Extra Roll', validators=[Optional(), NumberRange(min=0)])

    # --- Tabela de Cotas ---
    tabela_cotas = FileField(
        'Arquivo da Tabela de Cotas (.csv)',
        validators=[
            FileRequired("Por favor, selecione o arquivo de cotas."),
            FileAllowed(['csv'], 'Apenas arquivos .csv são permitidos!')
        ]
    )
    
    submit = SubmitField('Salvar Embarcação')