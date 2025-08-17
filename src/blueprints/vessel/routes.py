import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from flask_login import login_required, current_user
from .forms import VesselForm
from src.models import Vessel
from src.extensions import db

vessel_bp = Blueprint(
    'vessel', 
    __name__,
    template_folder='templates',
    url_prefix='/vessels' # Todas as rotas aqui começarão com /vessels
)

@vessel_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Exibe o formulário e processa o cadastro de uma nova embarcação."""
    print(f"--- ROTA /vessels/add ACESSADA (Método: {request.method}) ---")
    
    form = VesselForm()
    if form.validate_on_submit():
        print(">>> VALIDAÇÃO DO FORMULÁRIO BEM-SUCEDIDA <<<")
        print(f"Dados recebidos do formulário: {form.data}")
        
        try:
            # Lógica para salvar o arquivo de cotas
            arquivo_cotas = form.tabela_cotas.data
            filename = secure_filename(arquivo_cotas.filename)
            upload_path = os.path.join(current_app.root_path, '..', 'uploads', filename)
            print(f"Salvando arquivo em: {upload_path}")
            arquivo_cotas.save(upload_path)

            # Cria uma nova instância do modelo Vessel com os dados do formulário
            print("Criando objeto new_vessel...")
            new_vessel = Vessel(
                name=form.name.data,
                imo=form.imo.data,
                n_inscricao=form.n_inscricao.data,
                tipo=form.tipo.data,
                indicativo=form.indicativo.data,
                area_navegacao=form.area_navegacao.data,
                servico_1=form.servico_1.data,
                servico_2=form.servico_2.data,
                servico_3=form.servico_3.data,
                servico_4=form.servico_4.data,
                propulsada=(form.propulsada.data == 'True'),
                lpp=form.lpp.data,
                boca=form.boca.data,
                pontal=form.pontal.data,
                construction_year=form.construction_year.data,
                hull_material=form.hull_material.data,
                port_of_registry=form.port_of_registry.data,
                construction_location=form.construction_location.data,
                builder_shipyard=form.builder_shipyard.data,
                crew_number=form.crew_number.data,
                passenger_number=form.passenger_number.data,
                extra_roll_number=form.extra_roll_number.data,
                owner=current_user,
                tabela_cotas_filename=filename
            )
            
            print("Adicionando à sessão do DB...")
            db.session.add(new_vessel)
            print("Realizando commit no DB...")
            db.session.commit()
            print(">>> COMMIT BEM-SUCEDIDO! Embarcação salva. <<<")
            
            flash(f"Embarcação '{new_vessel.name}' cadastrada com sucesso!", 'success')
            return redirect(url_for('vessel.add'))
        
        except Exception as e:
            db.session.rollback() # Desfaz a tentativa de salvar
            print(f"!!! OCORREU UM ERRO DURANTE O COMMIT: {e} !!!")
            flash("Ocorreu um erro ao salvar a embarcação. Verifique os dados e tente novamente.", 'error')

    # Este bloco será executado se a validação falhar
    if form.errors:
        print(f">>> VALIDAÇÃO DO FORMULÁRIO FALHOU <<<")
        print(f"Erros de validação: {form.errors}")
        flash("O formulário contém erros. Por favor, corrija os campos indicados.", 'error')

    return render_template('add_vessel.html', form=form)