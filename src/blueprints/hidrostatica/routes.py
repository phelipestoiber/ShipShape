import os
import pandas as pd
import numpy as np
from flask import Blueprint, render_template, flash, current_app, request
from flask_login import login_required, current_user
from .forms import HydrostaticsCalculationForm
from src.models import Vessel
from src.core.interpolacao import Casco
from src.core.calculos_hidrostaticos import CalculadoraHidrostatica
# from src.core.visualizacao import plotar_curvas_hidrostaticas
from src.core.visualizacao import gerar_grafico_hidrostatico

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
    resultados_df = None
    curvas_plot_html = None
    resultados_html = None
    
    if form.validate_on_submit():
        try:
            # --- 1. Captura de dados e carregamento do casco ---
            # Captura dos dados do formulário
            vessel_id = form.vessel.data
            calc_method = form.calc_method.data
            metodo_interp = form.metodo_interp.data
            densidade = form.densidade.data
            calado_min_form = form.calado_min.data
            calado_max_form = form.calado_max.data

            # Carregamento do casco
            selected_vessel = Vessel.query.get(vessel_id)
            filepath = os.path.join(current_app.root_path, '..', 'uploads', selected_vessel.tabela_cotas_filename)
            tabela_de_cotas_df = pd.read_csv(filepath, header=None, names=['X', 'Y', 'Z'])
            casco = Casco(tabela_de_cotas_df, metodo=metodo_interp)
            # plot_html = casco.plotar_casco_3d()

            # --- 2. GERAÇÃO DA LISTA DE CALADOS A CALCULAR ---
            lista_de_calados_a_calcular = []

            print(f'Calado Mínimo: {calado_min_form}, Calado Máximo: {calado_max_form}')

            if calc_method == 'numero':
                num_calados = form.num_calados.data
                # Usa os valores do formulário em vez de 0.1 e calado_maximo_casco
                lista_de_calados_a_calcular = np.linspace(calado_min_form, calado_max_form, num_calados).tolist()
                print(f'Lista de Calados (Número): {lista_de_calados_a_calcular}')
            
            elif calc_method == 'incremento':
                inc_calados = form.inc_calados.data
                # Usa os valores do formulário em vez de 0.1 e calado_maximo_casco
                lista_de_calados_a_calcular = np.arange(calado_min_form, calado_max_form + inc_calados, inc_calados).tolist()
                print(f'Lista de Calados (Número): {lista_de_calados_a_calcular}')
            
            elif calc_method == 'manual':
                lista_calados_str = form.lista_calados.data
                lista_de_calados_a_calcular = [float(c.strip()) for c in lista_calados_str.split(';') if c.strip()]
                print(f'Lista de Calados (Número): {lista_de_calados_a_calcular}')

            # --- 3. EXECUÇÃO DOS CÁLCULOS ---
            if lista_de_calados_a_calcular:
                calculadora = CalculadoraHidrostatica(casco, densidade, metodo_interp)
                resultados_df = calculadora.calcular_curvas(lista_de_calados_a_calcular)

                print("\n=======================================================")
                print("======= T A B E L A   H I D R O S T Á T I C A =======")
                print("=======================================================")
                # .to_string() garante que todas as colunas e linhas sejam mostradas
                print(resultados_df.to_string())
                print("\n")

                if not resultados_df.empty:
                    resultados_html = resultados_df.to_html(
                        classes=['table', 'table-striped', 'table-hover'], # Classes CSS para estilo
                        index=False, # Não mostra o índice do DataFrame na tabela
                        float_format='{:.4f}'.format, # Formata os números decimais
                        table_id='tabela-resultados'
                    )

                    plot_html = gerar_grafico_hidrostatico(resultados_df, casco)

                flash(f"Cálculos para '{selected_vessel.name}' concluídos!", 'success')
            else:
                flash("Nenhum calado válido foi definido para o cálculo.", 'error')
                
        except Exception as e:
            flash(f"Ocorreu um erro ao processar os dados: {e}", 'error')

    # Se a requisição for um POST (submissão) e a validação acima falhou...
    elif request.method == 'POST':
        # Itera sobre todos os erros encontrados pelo formulário
        for field, errors in form.errors.items():
            for error in errors:
                # E cria um pop-up de erro para cada um
                flash(error, category='error')
            
    return render_template('index.html', form=form, plot_html=plot_html, resultados_html=resultados_html)