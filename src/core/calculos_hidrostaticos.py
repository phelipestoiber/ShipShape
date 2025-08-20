# src/core/calculos_hidrostaticos.py

import pandas as pd
import numpy as np
from scipy.integrate import quad
from scipy.optimize import fsolve
from scipy.interpolate import interp1d, PchipInterpolator
from .interpolacao import Casco


class PropriedadesHidrostaticas:
    """
    Calcula e armazena todas as propriedades hidrostáticas para um único calado.
    """
    def __init__(self, casco: Casco, calado: float, densidade: float, metodo_interp: str):
        self.casco = casco
        self.calado = calado
        self.densidade = densidade
        self.metodo_interp = metodo_interp
        
        # Dicionário para armazenar as áreas de cada seção
        self.areas_secoes = {}
        
        # Propriedades da linha d'água a serem calculadas
        self.x_re = None
        self.x_vante = None
        self.lwl = None # Comprimento na linha d'água
        self.bwl = None
        self.area_plano_flutuacao = None
        # ... e todas as outras propriedades ...

        self._calcular_todas_propriedades()

    def _calcular_dimensoes_linha_dagua(self):
        """
        Calcula as dimensões Lwl e Bwl para o calado atual.
        Adaptação do código procedural fornecido para a estrutura da classe.
        """
        # --- Cálculo da Boca na Linha d'Água (Bwl) ---
        meia_boca_max = 0.0
        for funcao_baliza in self.casco.funcoes_baliza.values():
            meia_boca_atual = np.nan_to_num(float(funcao_baliza(self.calado)))
            if meia_boca_atual > meia_boca_max:
                meia_boca_max = meia_boca_atual
        self.bwl = meia_boca_max * 2

        # --- Cálculo do Comprimento na Linha d'Água (Lwl) ---
        if self.casco.funcao_perfil:
            funcao_raiz = lambda x: self.casco.funcao_perfil(x) - self.calado
            
            x_lim_re = self.casco.funcao_perfil.x.min()
            x_lim_vante = self.casco.funcao_perfil.x.max()

            # Tenta encontrar as interseções com fsolve
            try:
                # Tenta encontrar a raiz iniciando a busca perto do limite de ré.
                # Um pequeno offset (1e-6) é usado para evitar problemas nos limites exatos.
                x_re_calc = fsolve(funcao_raiz, x0=x_lim_re + 1e-6)[0]
                if not (x_lim_re <= x_re_calc <= x_lim_vante): x_re_calc = x_lim_re
            except:
                x_re_calc = x_lim_re

            try:
                x_vante_calc = fsolve(funcao_raiz, x0=x_lim_vante - 1e-6)[0]
                if not (x_lim_re <= x_vante_calc <= x_lim_vante): x_vante_calc = x_lim_vante
            except:
                x_vante_calc = x_lim_vante

            self.x_re = min(x_re_calc, x_vante_calc)
            self.x_vante = max(x_re_calc, x_vante_calc)
            self.lwl = self.x_vante - self.x_re
        else:
            self.lwl = 0.0
            self.x_re = 0.0
            self.x_vante = 0.0

    def _calcular_area_secao(self, x_baliza: float) -> float:
        """
        Calcula a área submersa de uma única seção transversal (baliza)
        usando integração numérica.

        Args:
            x_baliza (float): A posição longitudinal (X) da baliza.

        Returns:
            float: A área da seção transversal submersa em metros quadrados.
        """
        # A função a ser integrada é 2 * meia_boca(z)
        # O 'quad' integra a função 'self.casco.obter_meia_boca'
        # desde z=0 (quilha aproximada) até z=self.calado.
        area, erro = quad(lambda z: self.casco.obter_meia_boca(x_baliza, z), 0, self.calado)
        
        # Multiplicamos por 2 para obter a área total (bombordo + estibordo)
        return area * 2
    
    def _calcular_area_plano_flutuacao(self):
        """
        Calcula a área do plano de flutuação (AWP), considerando casos
        especiais como popas de espelho (transom).
        """
        # 1. Filtra as balizas que estão estritamente DENTRO da linha d'água
        balizas_internas_x = [
            x for x in self.casco.posicoes_balizas 
            if x > self.x_re and x < self.x_vante
        ]
        balizas_internas_y = [self.casco.obter_meia_boca(x, self.calado) for x in balizas_internas_x]

        # 2. Lógica condicional para as extremidades (x_re e x_vante)
        baliza_popa_x = min(self.casco.posicoes_balizas)
        baliza_proa_x = max(self.casco.posicoes_balizas)
        tolerancia = 1e-3

        # Verifica a extremidade de ré
        if abs(self.x_re - baliza_popa_x) < tolerancia:
            y_re = self.casco.obter_meia_boca(baliza_popa_x, self.calado)
        else:
            y_re = 0.0

        # Verifica a extremidade de vante
        if abs(self.x_vante - baliza_proa_x) < tolerancia:
            y_vante = self.casco.obter_meia_boca(baliza_proa_x, self.calado)
        else:
            y_vante = 0.0

        # 3. Construir a lista final de pontos para a interpolação
        x_pontos = [self.x_re] + balizas_internas_x + [self.x_vante]
        y_pontos = [y_re] + balizas_internas_y + [y_vante]

        # --- DEBUGGER: Mostra os pontos que serão realmente usados ---
        print("\n--- INICIANDO DEPURAÇÃO: Pontos para Interpolação da AWP (Com Tolerância) ---")
        print("Pontos (X, Y) filtrados entre Xre={:.3f} e Xvante={:.3f}:".format(self.x_re, self.x_vante))
        for i in range(len(x_pontos)):
            print(f"  Ponto {i+1}: X = {x_pontos[i]:<7.4f}, Y (meia-boca) = {y_pontos[i]:.4f}")
        print("-----------------------------------------------------------------------------")
        
        # 4. Criação do Interpolador Final e Integração (sem alterações)
        if len(x_pontos) < 2:
            self.area_plano_flutuacao = 0.0
            return

        # Garante que não haja pontos X duplicados, o que pode quebrar o Pchip
        pontos_unicos = sorted(list(set(zip(x_pontos, y_pontos))))
        x_pontos_unicos = [p[0] for p in pontos_unicos]
        y_pontos_unicos = [p[1] for p in pontos_unicos]

        if self.metodo_interp == 'pchip':
            interpolador_wl = PchipInterpolator(x_pontos_unicos, y_pontos_unicos, extrapolate=False)
        else:
            interpolador_wl = interp1d(x_pontos_unicos, y_pontos_unicos, kind='linear', bounds_error=False, fill_value=0.0)

        meia_area, erro = quad(interpolador_wl, self.x_re, self.x_vante)
        self.area_plano_flutuacao = meia_area * 2

    def _calcular_todas_propriedades(self):
        """Método privado para chamar todos os outros cálculos na ordem correta."""
        print(f"\n--- Calculando propriedades para o calado T = {self.calado:.3f} m ---")
        
        # 1. Calcula as dimensões Lwl e Bwl (limites de integração)
        self._calcular_dimensoes_linha_dagua()

        # 2. Calcula a Área do Plano de Flutuação (AWP)
        self._calcular_area_plano_flutuacao()

        # 3. Itera sobre cada baliza para calcular sua área submersa
        for x_pos in self.casco.posicoes_balizas:
            area_secao = self._calcular_area_secao(x_pos)
            self.areas_secoes[x_pos] = area_secao


class CalculadoraHidrostatica:
    """
    Orquestra o cálculo das curvas hidrostáticas para uma faixa de calados.
    (Ainda não utilizada, mas já estruturada para o futuro)
    """
    def __init__(self, casco: Casco):
        self.casco = casco
        
    def calcular_curvas(self, lista_calados: list, densidade: float) -> pd.DataFrame:
        pass