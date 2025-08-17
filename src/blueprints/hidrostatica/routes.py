import os
import pandas as pd
from flask import Blueprint, render_template, flash, current_app
from flask_login import login_required, current_user
from .forms import HydrostaticsCalculationForm
from src.models import Vessel
from src.core.interpolacao import Casco

hidrostatica_bp = Blueprint('hidrostatica', __name__, template_folder='templates', url_prefix='/hidrostatica')

@hidrostatica_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = HydrostaticsCalculationForm()
    
    # Busca as embarcações do usuário logado para popular o DropDown
    user_vessels = Vessel.query.filter_by(user_id=current_user.id).order_by(Vessel.name).all()
    # Cria a lista de tuplas (id, nome) para as choices do formulário
    form.vessel.choices = [(v.id, v.name) for v in user_vessels]
    
    plot_html = None

    # Se o formulário for submetido e válido...
    if form.validate_on_submit():
        print("\n=======================================================")
        print(">>> FORMULÁRIO VÁLIDO. INICIANDO PROCESSAMENTO... <<<")
        print("=======================================================")

        try:
            # --- 1. Capturar os dados do formulário ---
            vessel_id = form.vessel.data
            calc_method = form.calc_method.data
            num_calados = form.num_calados.data
            inc_calados = form.inc_calados.data
            lista_calados = form.lista_calados.data
            metodo_interp = form.metodo_interp.data
            densidade = form.densidade.data

            # --- 2. Buscar a embarcação e o nome do arquivo no DB ---
            selected_vessel = Vessel.query.get(vessel_id)
            if not selected_vessel or not selected_vessel.tabela_cotas_filename:
                flash("Embarcação selecionada não encontrada ou não possui tabela de cotas.", 'error')
                return render_template('index.html', form=form)

            filename = selected_vessel.tabela_cotas_filename
            print(f"Embarcação selecionada: '{selected_vessel.name}' (ID: {vessel_id})")
            print(f"Arquivo de cotas associado: {filename}")

            # --- 3. Montar o caminho completo para o arquivo CSV ---
            filepath = os.path.join(current_app.root_path, '..', 'uploads', filename)
            
            if not os.path.exists(filepath):
                flash(f"Arquivo de cotas '{filename}' não encontrado no servidor.", 'error')
                return render_template('index.html', form=form)

            # --- 4. Carregar o arquivo CSV com o Pandas ---
            print("Tentando carregar o arquivo CSV com o Pandas...")
            # Assumindo que o CSV não tem cabeçalho (header=None) e as colunas são X, Y, Z
            tabela_de_cotas_df = pd.read_csv(filepath, header=None, names=['X', 'Y', 'Z'])
            print("Arquivo CSV carregado com sucesso!")

            # --- 4. Usando Classe Casco ---
            print("\nInstanciando a geometria do casco...")
            casco = Casco(tabela_de_cotas_df, metodo=metodo_interp)

            plot_html = casco.plotar_casco_3d()
            
            # --- 6. EXECUTE UM TESTE DE CÁLCULO ---
            # Vamos pegar a primeira baliza como exemplo para testar
            if casco.posicoes_balizas:
                primeira_baliza_x = casco.posicoes_balizas[0]
                altura_teste_z = 2.105  # Use um valor Z que esteja dentro do seu casco
                
                meia_boca_calculada = casco.obter_meia_boca(primeira_baliza_x, altura_teste_z)
                
                print("\n--- TESTE DE INTERPOLAÇÃO ---")
                print(f"  Calculando meia-boca para a baliza X={primeira_baliza_x} na altura Z={altura_teste_z}")
                print(f"  Resultado: Y = {meia_boca_calculada:.4f} m")
                print("-----------------------------\n")

            flash(f"Geometria de '{selected_vessel.name}' processada com sucesso!", 'success')
            
        except Exception as e:
            print(f"!!! OCORREU UM ERRO INESPERADO: {e} !!!")
            flash(f"Ocorreu um erro ao processar os dados: {e}", 'error')
        
    return render_template('index.html', form=form, plot_html=plot_html)