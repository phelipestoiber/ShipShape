# src/core/graficos.py

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from typing import List, Union

# Define o backend do matplotlib para ser compatível com Flet
matplotlib.use("svg")

def plotar_curvas(
    nomes_das_curvas: List[str],
    lista_de_series_x: List[List[Union[int, float]]],
    serie_y_comum: List[Union[int, float]],
    label_x: str,
    label_y: str,
    figsize: tuple
) -> plt.Figure:
    """
    Gera um gráfico com múltiplas curvas usando Matplotlib.

    Args:
        nomes_das_curvas (List[str]): Lista com os nomes de cada curva (para a legenda).
        lista_valores_x (List[Union[int, float]]): Lista com os valores do eixo X.
        lista_de_valores_y (List[List[Union[int, float]]]): Uma lista de listas, onde cada sub-lista contém os valores do eixo Y para uma curva.
        label_x (str): O rótulo do eixo X.
        label_y (str): O rótulo do eixo Y.

    Returns:
        plt.Figure: A figura do Matplotlib pronta para ser usada no Flet.
    """
    # Aplicado estilo para temas escuros. Isso ajusta automaticamente
    # a cor dos textos, eixos e da grade para serem visíveis em fundos escuros.
    plt.style.use('dark_background')

    # Cria a figura e os eixos do gráfico
    fig, ax = plt.subplots(figsize=figsize)

    # 3. Define fundo transparente para a figura e os eixos.
    # fig.patch.set_alpha(0.0)
    # ax.patch.set_alpha(0.0)

    # Itera sobre cada lista de valores Y para plotar uma curva
    for i, serie_x in enumerate(lista_de_series_x):
        ax.plot(serie_x, serie_y_comum, label=nomes_das_curvas[i], marker='o', linestyle='-')

    # --- Configuração dos Rótulos e Título ---
    ax.set_xlabel(label_x, fontsize=12)
    ax.set_ylabel(label_y, fontsize=12)
    ax.set_title(f"{label_y} vs. {label_x}", fontsize=14, weight='bold')

    # --- Configuração da Legenda ---
    # Coloca a legenda à direita, fora da área de plotagem
    ax.legend(title='Legenda', loc=0, fontsize='x-small')

    # --- Configuração dos Ticks (Marcadores dos Eixos) ---
    # Eixo X: Encontra até 10 intervalos "agradáveis".
    # 'prune' remove o primeiro ou último tick se eles ficarem muito perto das bordas.
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=10, prune='both'))
    # Adiciona os ticks menores automaticamente.
    ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
    # O formatador continua útil para garantir a precisão decimal.
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))

    # Eixo Y: Encontra até 10 intervalos "agradáveis" (geralmente queremos menos ticks no eixo Y).
    ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=10, prune='both'))
    ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:.2f}'))
    
    # Adiciona uma grade para facilitar a leitura
    ax.grid(True, which='major', linestyle='--', linewidth=0.5)
    ax.grid(True, which='minor', linestyle=':', linewidth=0.3)

    return fig