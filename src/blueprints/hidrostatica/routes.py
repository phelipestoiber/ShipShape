import os
import pandas as pd
from flask import Blueprint, render_template, flash, current_app
from flask_login import login_required, current_user
from .forms import HydrostaticsCalculationForm
from src.models import Vessel
from src.core.interpolacao import Casco
from src.core.calculos_hidrostaticos import PropriedadesHidrostaticas

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

            calado_de_teste = 2.31
            densidade = form.densidade.data
            
            print(f"\nInstanciando PropriedadesHidrostaticas para T = {calado_de_teste} m...")
            
            # Cria o objeto, que automaticamente executa os cálculos no __init__
            props_hidrostaticas = PropriedadesHidrostaticas(casco, calado_de_teste, densidade, metodo_interp)
            
            print("\n--- RESULTADO DO CÁLCULO DE ÁREAS DAS SEÇÕES ---")
            # Imprime o dicionário de áreas que foi calculado
            for baliza, area in props_hidrostaticas.areas_secoes.items():
                print(f"  Área da Baliza em X={baliza:<7.4f} m  =  {area:.4f} m²")
            print("---------------------------------------------------\n")

            # ----------------------------------------

            print("\n--- RESULTADO DO CÁLCULO DE DIMENSÕES DA LINHA D'ÁGUA ---")
            
            print(f"  Posição de Ré (Xre):   {props_hidrostaticas.x_re:.4f} m")
            print(f"  Posição de Vante (Xvante): {props_hidrostaticas.x_vante:.4f} m")
            print(f"  LWL:                    {props_hidrostaticas.lwl:.4f} m")
            print(f"  BWL:                    {props_hidrostaticas.bwl:.4f} m")
            print("----------------------------------------------------------\n")

            # ----------------------------------------

            print("\n--- RESULTADO DO CÁLCULO DA ÁREA DO PLANO DE FLUTUAÇÃO ---")
            print(f"  Área do Plano de Flutuação (AWP): {props_hidrostaticas.area_plano_flutuacao:.4f} m²")
            print("-----------------------------------------------------------\n")
            # ----------------------------------------
            
        except Exception as e:
            print(f"!!! OCORREU UM ERRO INESPERADO: {e} !!!")
            flash(f"Ocorreu um erro ao processar os dados: {e}", 'error')
        
    return render_template('index.html', form=form, plot_html=plot_html)