import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator, interp1d
import plotly.graph_objects as go

class Casco:
    """
    Representa a geometria do casco de uma embarcação, 
    permitindo a interpolação das suas formas.
    """
    def __init__(self, tabela_de_cotas_df: pd.DataFrame, metodo: str):
        """
        Inicializa o objeto Casco a partir de uma tabela de cotas.

        Args:
            tabela_de_cotas_df (pd.DataFrame): DataFrame com colunas 'X', 'Y', 'Z'.
        """
        print(f"-> Inicializando objeto Casco com método '{metodo}'...")
        self.df = tabela_de_cotas_df
        self.metodo = metodo
        
        # Identifica as posições únicas das balizas na direção X e as ordena
        self.posicoes_balizas = sorted(self.df['X'].unique())
        
        # Dicionário para armazenar as funções de interpolação de cada baliza
        self.funcoes_baliza = {}

        # Chama o método privado para criar as funções
        self._criar_interpoladores_balizas()
        self._criar_interpolador_perfil()

        print(f"-> Objeto Casco inicializado. {len(self.funcoes_baliza)} balizas interpoladas.")

    def _criar_interpoladores_balizas(self):
        """
        Método privado que itera sobre cada baliza e cria uma função 
        de interpolação para sua forma.
        """
        for x_val in self.posicoes_balizas:
            # Filtra o DataFrame para obter os pontos de uma única baliza
            df_baliza = self.df[self.df['X'] == x_val].sort_values('Z')
            
            # Pega os valores de Z (altura) e Y (meia-boca)
            z_coords = df_baliza['Z'].values
            y_coords = df_baliza['Y'].values

            # Evita erros se houver poucos pontos para interpolar
            if len(z_coords) > 1:
                # Cria a função de interpolação (Z -> Y)
                # fill_value=0 garante que fora do casco, a meia-boca seja 0
                if self.metodo == 'linear':
                    interpolador = interp1d(z_coords, y_coords, kind='linear', bounds_error=False, fill_value=0)
                
                else: # Padrão para 'pchip' ou qualquer outro valor
                    interpolador = PchipInterpolator(z_coords, y_coords, extrapolate=False)

                # Armazena a função no dicionário, usando a posição X como chave
                self.funcoes_baliza[x_val] = interpolador

    def _criar_interpolador_perfil(self):
        """
        Cria um interpolador para o perfil longitudinal da quilha (X -> Z).
        """
        print("-> Criando interpolador para o perfil do casco (linha da quilha)...")
        # Agrupa por X, pega a posição X e a altura mínima Z (quilha)
        dados_perfil = self.df.groupby('X').agg(Z_min=('Z', 'min')).reset_index()
        dados_perfil = dados_perfil.sort_values('X')
        
        if len(dados_perfil['X']) > 1:
            if self.metodo == 'linear':
                self.funcao_perfil = interp1d(dados_perfil['X'], dados_perfil['Z_min'], kind='linear', bounds_error=False, fill_value=0)
            else:
                self.funcao_perfil = PchipInterpolator(dados_perfil['X'], dados_perfil['Z_min'], extrapolate=False)


    def obter_meia_boca(self, x_baliza: float, z: float) -> float:
        """
        Calcula a meia-boca (valor Y) para uma dada baliza (X) e altura (Z).

        Args:
            x_baliza (float): A posição longitudinal (coordenada X) da baliza.
            z (float): A altura (coordenada Z) na qual se deseja a meia-boca.

        Returns:
            float: O valor da meia-boca (Y). Retorna 0 se a baliza não existir 
                   ou se a altura Z estiver fora do range definido.
        """
        funcao_interpoladora = self.funcoes_baliza.get(x_baliza)
        
        if funcao_interpoladora:
            # Usa a função de interpolação para encontrar Y no ponto Z
            meia_boca = funcao_interpoladora(z)
            # Retorna 0 se o resultado for NaN (ocorre com extrapolate=False)
            return np.nan_to_num(meia_boca)
        else:
            # Se a baliza exata não existir no dicionário, retorna 0
            return 0.0
        
    def plotar_balizas(self) -> str:
        """
        Gera um gráfico interativo das seções de baliza usando o Plotly.

        Returns:
            str: Uma string contendo o HTML/JS do gráfico Plotly.
        """
        print("-> Gerando gráfico de balizas com Plotly...")
        fig = go.Figure()

        # Itera sobre cada baliza para adicioná-la ao gráfico
        for x_val in self.posicoes_balizas:
            # Pega os pontos originais da tabela de cotas para a baliza
            df_baliza = self.df[self.df['X'] == x_val].sort_values('Z')
            
            # Adiciona os pontos originais (lado direito do casco)
            fig.add_trace(go.Scatter(
                x=df_baliza['Y'], 
                y=df_baliza['Z'],
                mode='lines+markers',
                name=f'Baliza X={x_val:.2f}'
            ))
            
            # Adiciona a imagem espelhada (lado esquerdo do casco)
            fig.add_trace(go.Scatter(
                x=-df_baliza['Y'], # Inverte o sinal de Y para espelhar
                y=df_baliza['Z'],
                mode='lines',
                line=dict(color=fig.data[-1].line.color), # Usa a mesma cor da linha original
                showlegend=False # Não precisa de legenda para a parte espelhada
            ))

        # Configurações de layout do gráfico
        fig.update_layout(
            title='Seções Transversais do Casco (Balizas)',
            xaxis_title='Meia-Boca (Y)',
            yaxis_title='Altura (Z)',
            yaxis=dict(scaleanchor="x", scaleratio=1), # Garante que as proporções sejam realistas
            template='plotly_white'
        )
        
        print("-> Gráfico gerado. Convertendo para HTML.")
        # Converte o gráfico para uma div HTML
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def plotar_casco_3d(self) -> str:
        """
        Gera um gráfico 3D mostrando os pontos originais do CSV e
        as curvas interpoladas do casco e do perfil.
        """
        print("-> Gerando gráfico 3D (pontos + interpoladores)...")
        
        # --- 1. Preparar os dados dos PONTOS originais ---
        df_sem_centro = self.df[self.df['Y'] > 0]
        # Combina pontos de estibordo e bombordo
        pontos_x = list(pd.concat([self.df['X'], df_sem_centro['X']]))
        pontos_y = list(pd.concat([self.df['Y'], -df_sem_centro['Y']]))
        pontos_z = list(pd.concat([self.df['Z'], df_sem_centro['Z']]))
        
        # Cria o traço para a nuvem de pontos
        trace_pontos = go.Scatter3d(
            x=pontos_x, y=pontos_y, z=pontos_z,
            mode='markers',
            marker=dict(size=2, color='green'), # Pontos verdes
            name='Pontos do CSV'
        )

        # --- 2. Preparar os traços das LINHAS interpoladas ---
        
        # Lista para guardar todos os traços de linhas
        traces_linhas = []
        
        # Linhas das Balizas
        for x_val in self.posicoes_balizas:
            interpolador = self.funcoes_baliza.get(x_val)
            if interpolador:
                z_coords_orig = self.df[self.df['X'] == x_val]['Z']
                z_interp = np.linspace(z_coords_orig.min(), z_coords_orig.max(), 50)
                y_interp = interpolador(z_interp)
                
                nome_da_legenda = f'Baliza {x_val:.2f}'
                
                # Linha de estibordo (direita)
                traces_linhas.append(go.Scatter3d(
                    x=[x_val] * 50, y=list(y_interp), z=list(z_interp),
                    mode='lines', line=dict(color='green', width=3),
                    name=nome_da_legenda,
                    legendgroup=nome_da_legenda
                ))
                # Linha de bombordo (esquerda)
                traces_linhas.append(go.Scatter3d(
                    x=[x_val] * 50, y=list(-y_interp), z=list(z_interp),
                    mode='lines', line=dict(color='green', width=3),
                    showlegend=False,
                    legendgroup=nome_da_legenda
                ))
        
        # Linha do Perfil da Quilha
        if self.funcao_perfil:
            x_interp = list(np.linspace(min(self.posicoes_balizas), max(self.posicoes_balizas), 100))
            z_interp = list(self.funcao_perfil(x_interp))
            traces_linhas.append(go.Scatter3d(
                x=x_interp, y=[0] * len(x_interp), z=z_interp,
                mode='lines', line=dict(color='royalblue', width=3),
                name='Perfil da Quilha'
            ))

        # --- 3. Cria a Figura com todos os traços ---
        # A ordem é importante: desenha os pontos primeiro, depois as linhas por cima
        fig = go.Figure(data=[trace_pontos] + traces_linhas)

        # Configura o layout da cena 3D
        fig.update_layout(
            title_text='Visualização 3D do Casco (Pontos e Curvas)',
            scene=dict(
                xaxis_title='Comprimento (X)',
                yaxis_title='Boca (Y)',
                zaxis_title='Altura (Z)',
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        print("-> Objeto de gráfico 3D gerado. Convertendo para HTML.")
        return fig.to_html(full_html=False, include_plotlyjs=False)
