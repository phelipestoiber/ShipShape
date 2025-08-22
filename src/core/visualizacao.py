import pandas as pd
import plotly.graph_objects as go

# def plotar_curvas_hidrostaticas(df: pd.DataFrame) -> str:
#     """
#     Gera um gráfico 2D interativo com um DropDown para selecionar
#     qual curva hidrostática exibir.

#     Args:
#         df (pd.DataFrame): A tabela de resultados (DataFrame) dos cálculos.

#     Returns:
#         str: Uma string contendo o HTML/JS do gráfico Plotly.
#     """

#     # ===============================================================
#     # === MODO DE DEPURAÇÃO: Alterne para False para usar dados reais ===
#     DEBUG_MODE = False 
#     # ===============================================================

#     if DEBUG_MODE:
#         print("--- MODO DE DEPURAÇÃO ATIVADO: Gerando gráfico com dados de exemplo. ---")
#         fig = go.Figure()
#         fig.add_trace(go.Scatter(
#             x=[1, 2, 3, 4, 5, 6], 
#             y=[10, 11, 12, 13, 14, 15],
#             mode='lines+markers',
#             name='Teste de Dados'
#         ))
#         fig.update_layout(
#             title="Gráfico de Teste com Dados de Exemplo",
#             xaxis_title="Eixo X de Teste",
#             yaxis_title="Eixo Y de Teste"
#         )
#         return fig.to_html(full_html=False, include_plotlyjs=False)
    
#     # --- DEBUGGER: Inspecionando os dados recebidos ---
#     print("\n--- INICIANDO DEPURAÇÃO: plotar_curvas_hidrostaticas ---")
#     print("Colunas REAIS recebidas no DataFrame:")
#     print(df.columns.tolist())
#     print("----------------------------------------------------------")
#     # ---------------------------------------------------

#     if df is None or df.empty:
#         return "<div class='placeholder'>Dados insuficientes para gerar o gráfico.</div>"

#     print("-> Gerando gráfico de curvas hidrostáticas...")
#     fig = go.Figure()

#     # Colunas que queremos plotar
#     colunas_plotaveis = [
#         'Volume (m³)', 'Desloc. (t)', 'AWP (m²)', 'LWL (m)', 'BWL (m)', 
#         'LCB (m)', 'VCB (m)', 'LCF (m)', 'BMt (m)', 'KMt (m)', 
#         'BMl (m)', 'KMl (m)', 'TPC (t/cm)', 'MTc (t·m/cm)',
#         'Cb', 'Cp', 'Cwp', 'Cm'
#     ]

#     eixo_y_coluna = 'Calado (m)'

#     # --- DEBUGGER: Verificando a coluna do eixo Y ---
#     if eixo_y_coluna not in df.columns:
#         print(f"!!! ERRO CRÍTICO: A coluna do eixo Y '{eixo_y_coluna}' não foi encontrada no DataFrame. !!!")
#         return "<div class='placeholder'>Erro: Coluna de Calado não encontrada.</div>"
#     # -----------------------------------------------

#     # 1. Adiciona um traço (uma linha) para cada propriedade
#     for i, coluna in enumerate(colunas_plotaveis):
#         if coluna in df.columns:
#             fig.add_trace(
#                 go.Scatter(
#                     x=df[coluna],
#                     y=df[eixo_y_coluna],
#                     name=coluna,
#                     # Deixa apenas a primeira curva visível por padrão
#                     visible=(i == 0)
#                 )
#             )
#         else:
#             # --- DEBUGGER: Avisa se uma coluna não for encontrada ---
#             print(f"-> AVISO: A coluna '{coluna}' não foi encontrada no DataFrame e será pulada.")
#             # ----------------------------------------------------


#     # 2. Cria os botões para o DropDown
#     botoes = []
#     for i, coluna in enumerate(colunas_plotaveis):
#         # Cria uma lista de 'visibilidade' (ex: [True, False, False, ...])
#         visibilidade = [False] * len(colunas_plotaveis)
#         visibilidade[i] = True # Torna apenas a curva atual visível
        
#         botoes.append(
#             dict(
#                 method='restyle',
#                 label=coluna,
#                 args=[{'visible': visibilidade},
#                       {'xaxis.title': coluna}] # Atualiza o título do eixo X
#             )
#         )

#     # 3. Adiciona o menu DropDown ao layout do gráfico
#     fig.update_layout(
#         updatemenus=[
#             dict(
#                 active=0, # O primeiro botão é o ativo
#                 buttons=botoes,
#                 direction="down",
#                 pad={"r": 10, "t": 10},
#                 showactive=True,
#                 x=0.01,
#                 xanchor="left",
#                 y=1.15,
#                 yanchor="top"
#             )
#         ],
#         title="Curvas Hidrostáticas",
#         xaxis_title=colunas_plotaveis[0], # Título inicial do eixo X
#         yaxis_title=eixo_y_coluna
#     )
    
#     print("-> Gráfico de curvas gerado.")
#     return fig.to_html(full_html=False, include_plotlyjs=False)

def plotar_curvas_hidrostaticas(df: pd.DataFrame) -> str:
    """
    Gera um gráfico 2D interativo com um DropDown (versão final e robusta).
    """
    if df is None or df.empty:
        return "<div class='placeholder'>Dados insuficientes para gerar o gráfico.</div>"

    fig = go.Figure()

    # Lista de colunas a serem plotadas, na ordem desejada
    colunas_plotaveis = [
        'Volume (m³)', 'Desloc. (t)', 'AWP (m²)', 'LWL (m)', 'BWL (m)', 'LCB (m)', 
        'VCB (m)', 'LCF (m)', 'BMt (m)', 'KMt (m)', 'BMl (m)', 'KMl (m)', 
        'TPC (t/cm)', 'MTc (t·m/cm)', 'Cb', 'Cp', 'Cwp', 'Cm'
    ]
    # Eixo Y sempre será o calado
    eixo_y_coluna = 'Calado (m)'

    if eixo_y_coluna not in df.columns:
        return f"<div class='placeholder'>Erro: Coluna de Calado '{eixo_y_coluna}' não foi encontrada.</div>"

    # 1. Adiciona todos os traços que existem no DataFrame
    # Apenas o primeiro que for adicionado com sucesso ficará visível
    primeiro_visivel_adicionado = False
    for coluna in colunas_plotaveis:
        if coluna in df.columns:
            visible_status = False
            if not primeiro_visivel_adicionado:
                visible_status = True
                primeiro_visivel_adicionado = True
            
            fig.add_trace(go.Scatter(x=df[coluna], y=df[eixo_y_coluna], name=coluna, visible=visible_status))

    # 2. Cria os botões COM BASE NOS TRAÇOS QUE REALMENTE EXISTEM (fig.data)
    botoes = []
    # Itera sobre os traços que foram de fato adicionados à figura
    for i, trace in enumerate(fig.data):
        # Cria uma lista de visibilidade com o tamanho exato do número de traços
        visibilidade = [False] * len(fig.data)
        visibilidade[i] = True # Ativa apenas o traço correspondente a este botão
        
        botoes.append(
            dict(
                method='restyle',
                label=trace.name, # Pega o nome do próprio traço
                args=[{'visible': visibilidade},
                      {'xaxis.title': trace.name}] # Atualiza o título do eixo X
            )
        )

    # 3. Adiciona o menu DropDown ao layout
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=botoes,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.01, xanchor="left", y=1.15, yanchor="top"
        )],
        title="Curvas Hidrostáticas",
        xaxis_title=fig.data[0].name if fig.data else "Valores",
        yaxis_title=eixo_y_coluna
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=False)
