# src/models/vessel.py

from src.extensions import db

class Vessel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    imo = db.Column(db.Integer, nullable=True) # Opcional no form -> nullable=True
    n_inscricao = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    indicativo = db.Column(db.String(50), nullable=True) # Opcional no form -> nullable=True
    area_navegacao = db.Column(db.String(50), nullable=False)
    servico_1 = db.Column(db.String(50), nullable=False) # Obrigatório
    servico_2 = db.Column(db.String(50), nullable=True)  # Opcional
    servico_3 = db.Column(db.String(50), nullable=True)  # Opcional
    servico_4 = db.Column(db.String(50), nullable=True)  # Opcional
    propulsada = db.Column(db.Boolean, default=False)
    lpp = db.Column(db.Float, nullable=False)
    boca = db.Column(db.Float, nullable=False)
    pontal = db.Column(db.Float, nullable=False)
    construction_year = db.Column(db.Integer, nullable=False)
    hull_material = db.Column(db.String(50), nullable=False)
    port_of_registry = db.Column(db.String(50), nullable=False)
    construction_location = db.Column(db.String(100), nullable=False)
    builder_shipyard = db.Column(db.String(100), nullable=False)
    crew_number = db.Column(db.Integer, nullable=True)
    passenger_number = db.Column(db.Integer, nullable=True)
    extra_roll_number = db.Column(db.Integer, nullable=True)
    
    tabela_cotas_filename = db.Column(db.String(255), nullable=False) # O arquivo é obrigatório pelo form

    # Chave estrangeira para ligar a embarcação a um usuário
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relação de volta para o usuário
    owner = db.relationship('User', back_populates='vessels')