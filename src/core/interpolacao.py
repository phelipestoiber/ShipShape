import pandas as pd
from scipy.interpolate import PchipInterpolator, interp1d

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
