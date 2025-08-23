import pandas as pd
import plotly.graph_objects as go
import numpy as np
from .interpolacao import Casco 

def gerar_grafico_hidrostatico(df_resultados: pd.DataFrame, casco: Casco) -> str:
    """
    Gera um gráfico interativo com um DropDown para alternar entre a visualização
    3D do casco e as curvas hidrostáticas 2D.
    """
    fig = go.Figure()
    
    # --- Passo 1: Criar TODOS os traços ---
    
    # Traços para o CASCO 3D (com legendgroup)
    traces_3d = []
    # Pontos
    df_sem_centro = casco.df[casco.df['Y'] > 0]
    pontos_x = list(pd.concat([casco.df['X'], df_sem_centro['X']]))
    pontos_y = list(pd.concat([casco.df['Y'], -df_sem_centro['Y']]))
    pontos_z = list(pd.concat([casco.df['Z'], df_sem_centro['Z']]))
    traces_3d.append(go.Scatter3d(x=pontos_x, y=pontos_y, z=pontos_z, mode='markers', marker=dict(size=2, color='green'), name='Pontos CSV', visible=False))
    # Linhas Balizas 3D
    for x_val in casco.posicoes_balizas:
        interpolador = casco.funcoes_baliza.get(x_val)
        if interpolador:
            z_coords_orig = casco.df[casco.df['X'] == x_val]['Z']
            z_interp = np.linspace(z_coords_orig.min(), z_coords_orig.max(), 50)
            y_interp = interpolador(z_interp)
            
            nome_da_legenda = f'Baliza {x_val:.2f}'
            # Linha de estibordo (direita)
            traces_3d.append(go.Scatter3d(
                x=[x_val]*50, y=list(y_interp), z=list(z_interp), mode='lines', 
                line=dict(color='green'), name=nome_da_legenda, legendgroup=nome_da_legenda, visible=False
            ))
            # Linha de bombordo (esquerda)
            traces_3d.append(go.Scatter3d(
                x=[x_val]*50, y=list(-y_interp), z=list(z_interp), mode='lines', 
                line=dict(color='green'), showlegend=False, legendgroup=nome_da_legenda, visible=False
            ))
    # Linha Perfil 3D
    if casco.funcao_perfil:
        x_interp = np.linspace(min(casco.posicoes_balizas), max(casco.posicoes_balizas), 100)
        z_interp = casco.funcao_perfil(x_interp)
        traces_3d.append(go.Scatter3d(x=list(x_interp), y=[0]*100, z=list(z_interp), mode='lines', line=dict(color='royalblue', width=3), name='Perfil 3D', visible=False))

    # Traços para as CURVAS HIDROSTÁTICAS 2D
    traces_2d_curvas = []
    eixo_y_coluna = 'Calado (m)'
    colunas_hidro = [col for col in df_resultados.columns if col != eixo_y_coluna]
    for coluna in colunas_hidro:
        traces_2d_curvas.append(go.Scatter(x=list(df_resultados[coluna]), y=list(df_resultados[eixo_y_coluna]), name=coluna, visible=False))

    fig.add_traces(traces_3d + traces_2d_curvas)

    # --- Passo 2: Criar os botões do DropDown ---
    botoes = []
    
    # Botão para o Gráfico 3D
    layout_3d = {
        'title': 'Visualização 3D do Casco',
        'scene': {
            'visible': True,
            'aspectmode': 'data',  # <-- A CORREÇÃO CRÍTICA ESTÁ AQUI
            'xaxis': {'title': 'Comprimento (X)'},
            'yaxis': {'title': 'Boca (Y)'},
            'zaxis': {'title': 'Altura (Z)'}
        },
        'xaxis': {'visible': False},
        'yaxis': {'visible': False}
    }

    visibilidade_3d = [True] * len(traces_3d) + [False] * len(traces_2d_curvas)
    botoes.append(dict(method='update', label='Casco 3D', args=[{'visible': visibilidade_3d}, layout_3d]))

    # Botões para cada Curva Hidrostática 2D
    for i, trace in enumerate(traces_2d_curvas):
        visibilidade = [False] * len(fig.data)
        visibilidade[len(traces_3d) + i] = True
        layout_2d = {
            'title': f'Curva de {trace.name}',
            'scene': {'visible': False},
            'xaxis': {'visible': True, 'title': trace.name},
            'yaxis': {'visible': True, 'title': eixo_y_coluna}
        }
        botoes.append(dict(method='update', label=trace.name, args=[{'visible': visibilidade}, layout_2d]))

    # --- Passo 3: Adicionar o menu e o layout ---
    fig.update_layout(
        updatemenus=[dict(
            active=0, buttons=botoes, direction="down",
            pad={"r": 10, "t": 10}, showactive=True,
            x=1.007, xanchor="right", y=1.01, yanchor="bottom"
        )],
        title="Visualizador de Curvas e Geometria",
        paper_bgcolor="#f0f1e6",
    )

    # Define a CENA 3D (para quando os traços 3D estiverem visíveis)
    dbg3d = dict(
        showbackground = True, 
        backgroundcolor ="rgb(200, 200, 230)", 
        gridcolor = "rgb(200, 200, 230)",  
        zeroline = False)
    
    fig.update_layout(
        scene=dict(
            aspectmode='data', 
            xaxis_title='Comprimento (X)', 
            yaxis_title='Boca (Y)', 
            zaxis_title='Altura (Z)',
            ),
        template='plotly_white',
        margin=dict(t=10, b=10, l=10, r=10),
    )
    
    # Ativa a primeira opção ("Casco 3D") por padrão
    for trace in traces_3d:
        trace.visible = True

    return fig.to_html(full_html=False, include_plotlyjs=False)