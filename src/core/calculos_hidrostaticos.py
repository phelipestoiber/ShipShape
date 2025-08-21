# src/core/calculos_hidrostaticos.py

import pandas as pd
import numpy as np
from scipy.integrate import quad
from scipy.optimize import fsolve
from scipy.interpolate import interp1d, PchipInterpolator
from .interpolacao import Casco
import concurrent.futures
import time


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

        self.interpolador_wl = None
        self.area_plano_flutuacao = None

        self.interpolador_areas = None
        self.volume = None
        self.deslocamento = None

        self.lcf = None

        self.lcb = None

        self.vcb = None

        self.momento_inercia_transversal = None

        self.momento_inercia_longitudinal = None

        self.bmt = None # Raio Metacêntrico Transversal
        self.kmt = None # Altura Metacêntrica Transversal
        self.bml = None # Raio Metacêntrico Longitudinal
        self.kml = None # Altura Metacêntrica Longitudinal
        self.tpc = None # Toneladas por Centímetro de Imersão
        self.mtc = None # Momento para Alterar o Trim em 1 cm
        self.cb = None  # Coeficiente de Bloco
        self.cp = None  # Coeficiente Prismático
        self.cwp = None # Coeficiente do Plano de Flutuação
        self.cm = None  # Coeficiente de Seção Mestra

        

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
        
        # 4. Criação do Interpolador Final e Integração
        if len(x_pontos) < 2:
            self.area_plano_flutuacao = 0.0
            self.interpolador_wl = None
            return

        pontos_unicos = sorted(list(set(zip(x_pontos, y_pontos))))
        x_pontos_unicos = [p[0] for p in pontos_unicos]
        y_pontos_unicos = [p[1] for p in pontos_unicos]

        if self.metodo_interp == 'pchip':
            self.interpolador_wl = PchipInterpolator(x_pontos_unicos, y_pontos_unicos, extrapolate=False)
        else:
            self.interpolador_wl = interp1d(x_pontos_unicos, y_pontos_unicos, kind='linear', bounds_error=False, fill_value=0.0)

        meia_area, erro = quad(self.interpolador_wl, self.x_re, self.x_vante)
        self.area_plano_flutuacao = meia_area * 2

    def _calcular_volume_deslocamento(self):
        """
        Calcula o volume submerso e o deslocamento para o calado atual,
        considerando as áreas das seções nas extremidades da linha d'água.
        """
        # 1. Filtra as balizas que estão estritamente DENTRO da linha d'água
        x_internos = [
            x for x in self.casco.posicoes_balizas
            if x > self.x_re and x < self.x_vante
        ]
        areas_internas = [self.areas_secoes[x] for x in x_internos]

        # 2. Lógica condicional para as extremidades (x_re e x_vante)
        baliza_popa_x = min(self.casco.posicoes_balizas)
        baliza_proa_x = max(self.casco.posicoes_balizas)
        tolerancia = 1e-3

        # Verifica a extremidade de ré
        if abs(self.x_re - baliza_popa_x) < tolerancia:
            # Se x_re coincide com a baliza de popa, usa a área daquela baliza
            area_re = self.areas_secoes.get(baliza_popa_x, 0.0)
        else:
            # Caso contrário, a área na interseção é zero
            area_re = 0.0

        # Verifica a extremidade de vante
        if abs(self.x_vante - baliza_proa_x) < tolerancia:
            # Se x_vante coincide com a baliza de proa, usa a área daquela baliza
            area_vante = self.areas_secoes.get(baliza_proa_x, 0.0)
        else:
            # Caso contrário, a área na interseção é zero
            area_vante = 0.0

        # 3. Constrói a lista final de pontos para a interpolação
        x_pontos = [self.x_re] + x_internos + [self.x_vante]
        areas_pontos = [area_re] + areas_internas + [area_vante]

        # --- DEBUGGER (sem alterações) ---
        # print("\n--- INICIANDO DEPURAÇÃO: Pontos para Interpolação do Volume (Com Tolerância) ---")
        # print("Pontos (X, Área) filtrados entre Xre={:.3f} e Xvante={:.3f}:".format(self.x_re, self.x_vante))
        # for i in range(len(x_pontos)):
        #     print(f"  Ponto {i+1}: X = {x_pontos[i]:<7.4f}, Área = {areas_pontos[i]:.4f} m²")
        # print("---------------------------------------------------------------------------------")
        
        # 4. Criação do Interpolador e Integração (sem alterações)
        if len(x_pontos) < 2:
            self.volume = 0.0
            self.deslocamento = 0.0
            return

        pontos_unicos = sorted(list(set(zip(x_pontos, areas_pontos))))
        x_pontos_unicos = [p[0] for p in pontos_unicos]
        areas_pontos_unicos = [p[1] for p in pontos_unicos]

        # Cria o interpolador e o ARMAZENA no atributo da classe
        if self.metodo_interp == 'pchip':
            self.interpolador_areas = PchipInterpolator(x_pontos_unicos, areas_pontos_unicos, extrapolate=False)
        else:
            self.interpolador_areas = interp1d(x_pontos_unicos, areas_pontos_unicos, kind='linear', bounds_error=False, fill_value=0.0)
        
        # Integração Numérica usando o interpolador recém-criado
        volume_calculado, erro = quad(self.interpolador_areas, self.x_re, self.x_vante)

        self.volume = volume_calculado
        self.deslocamento = self.volume * self.densidade

    def _calcular_lcf(self):
        """
        Calcula a posição longitudinal do centro de flutuação (LCF).
        """
        # Se a área for nula ou o interpolador não existir, o LCF é indefinido (ou 0)
        if self.area_plano_flutuacao == 0.0 or not self.interpolador_wl:
            self.lcf = 0.0
            return
            
        # 1. Define a função a ser integrada: x * y(x)
        funcao_momento_longitudinal = lambda x: x * self.interpolador_wl(x)
        
        # 2. Integra para obter o momento longitudinal da meia-área
        momento_long_meia_area, erro = quad(funcao_momento_longitudinal, self.x_re, self.x_vante)
        
        # 3. Calcula a meia-área
        meia_area = self.area_plano_flutuacao / 2
        
        # 4. LCF é o momento dividido pela área
        # Previne divisão por zero, embora a primeira verificação já deva cuidar disso.
        if meia_area > 1e-6:
            self.lcf = momento_long_meia_area / meia_area
        else:
            self.lcf = 0.0

    def _calcular_lcb(self):
        """
        Calcula a posição longitudinal do centro de carena (LCB).
        """
        # Se o volume for nulo ou o interpolador não existir, o LCB é indefinido (ou 0)
        if self.volume == 0.0 or not self.interpolador_areas:
            self.lcb = 0.0
            return
            
        # 1. Define a função a ser integrada: x * A(x)
        funcao_momento_longitudinal = lambda x: x * self.interpolador_areas(x)
        
        # 2. Integra para obter o momento longitudinal do volume
        momento_long_volume, erro = quad(funcao_momento_longitudinal, self.x_re, self.x_vante)
        
        # 3. LCB é o momento dividido pelo volume
        if abs(self.volume) > 1e-6:
            self.lcb = momento_long_volume / self.volume
        else:
            self.lcb = 0.0

    def _calcular_momento_vertical_secao(self, x_baliza: float) -> float:
        """
        Calcula o momento de área vertical de uma única seção transversal.
        Integral de z * 2y(z) dz
        """
        # A função a ser integrada é: z * (2 * meia_boca(z))
        funcao_momento = lambda z: z * 2 * self.casco.obter_meia_boca(x_baliza, z)
        
        # Integra de 0 até o calado atual
        momento_vertical, erro = quad(funcao_momento, 0, self.calado)
        return momento_vertical

    def _calcular_vcb(self):
        """
        Calcula a posição vertical do centro de carena (VCB) pela
        integração dos momentos verticais das seções.
        """
        if self.volume == 0.0:
            self.vcb = 0.0
            return

        # 1. Calcula o momento vertical para cada baliza
        momentos_verticais = {}
        for x_pos in self.casco.posicoes_balizas:
            momentos_verticais[x_pos] = self._calcular_momento_vertical_secao(x_pos)
            
        # 2. Cria um interpolador para a curva de momentos verticais (Momento = f(x))
        x_pontos = list(momentos_verticais.keys())
        momentos_pontos = list(momentos_verticais.values())
        
        pontos_ordenados = sorted(zip(x_pontos, momentos_pontos))
        x_pontos_sorted = [p[0] for p in pontos_ordenados]
        momentos_pontos_sorted = [p[1] for p in pontos_ordenados]
        
        if self.metodo_interp == 'pchip':
            interpolador_momentos = PchipInterpolator(x_pontos_sorted, momentos_pontos_sorted, extrapolate=False)
        else:
            interpolador_momentos = interp1d(x_pontos_sorted, momentos_pontos_sorted, kind='linear', bounds_error=False, fill_value=0.0)

        # 3. Integra a curva de momentos ao longo do comprimento para obter o momento total do volume
        momento_total_vertical, erro = quad(interpolador_momentos, self.x_re, self.x_vante)

        # 4. VCB é o momento vertical total dividido pelo volume
        if abs(self.volume) > 1e-6:
            self.vcb = momento_total_vertical / self.volume
        else:
            self.vcb = 0.0

    # # --- NOVO MÉTODO AUXILIAR ---
    # def _calcular_momento_vertical_secao(self, x_baliza: float) -> float:
    #     """
    #     Calcula o momento de área vertical de uma única seção transversal em
    #     relação à quilha (z=0). Integral de z * 2y(z) dz.
    #     """
    #     # A função a ser integrada é: z * largura_da_secao(z)
    #     funcao_momento = lambda z: z * 2 * self.casco.obter_meia_boca(x_baliza, z)
        
    #     # Integra de 0 (quilha) até o calado atual
    #     momento_vertical, erro = quad(funcao_momento, 0, self.calado)
    #     return momento_vertical

    # # --- MÉTODO _CALCULAR_VCB REESCRITO ---
    # def _calcular_vcb(self):
    #     """
    #     Calcula a posição vertical do centro de carena (VCB) pela
    #     integração longitudinal dos momentos verticais das seções.
    #     """
    #     if self.volume == 0.0:
    #         self.vcb = 0.0
    #         return

    #     # 1. Calcula o momento vertical para cada baliza do casco
    #     momentos_verticais_secoes = {
    #         x: self._calcular_momento_vertical_secao(x) 
    #         for x in self.casco.posicoes_balizas
    #     }

    #     # 2. Filtra as balizas que estão estritamente DENTRO da linha d'água
    #     x_internos = [x for x in self.casco.posicoes_balizas if x > self.x_re and x < self.x_vante]
    #     momentos_internos = [momentos_verticais_secoes[x] for x in x_internos]

    #     # 3. Lógica condicional para os momentos nas extremidades
    #     baliza_popa_x = min(self.casco.posicoes_balizas)
    #     baliza_proa_x = max(self.casco.posicoes_balizas)
    #     tolerancia = 1e-3

    #     momento_re = momentos_verticais_secoes.get(baliza_popa_x, 0.0) if abs(self.x_re - baliza_popa_x) < tolerancia else 0.0
    #     momento_vante = momentos_verticais_secoes.get(baliza_proa_x, 0.0) if abs(self.x_vante - baliza_proa_x) < tolerancia else 0.0

    #     # 4. Constrói a lista final de pontos para a interpolação da curva de momentos
    #     x_pontos = [self.x_re] + x_internos + [self.x_vante]
    #     momentos_pontos = [momento_re] + momentos_internos + [momento_vante]

    #     # 5. Criação do Interpolador (MomentoVertical = f(x)) e Integração
    #     if len(x_pontos) < 2:
    #         self.vcb = 0.0
    #         return
            
    #     pontos_unicos = sorted(list(set(zip(x_pontos, momentos_pontos))))
    #     x_pontos_unicos = [p[0] for p in pontos_unicos]
    #     momentos_pontos_unicos = [p[1] for p in pontos_unicos]

    #     if self.metodo_interp == 'pchip':
    #         interpolador_momentos = PchipInterpolator(x_pontos_unicos, momentos_pontos_unicos, extrapolate=False)
    #     else:
    #         interpolador_momentos = interp1d(x_pontos_unicos, momentos_pontos_unicos, kind='linear', bounds_error=False, fill_value=0.0)
        
    #     momento_total_vertical, erro = quad(interpolador_momentos, self.x_re, self.x_vante)

    #     # 6. VCB é o momento vertical total do volume, dividido pelo volume
    #     if abs(self.volume) > 1e-6:
    #         self.vcb = momento_total_vertical / self.volume
    #     else:
    #         self.vcb = 0.0

    def _calcular_momento_inercia_transversal(self):
        """
        Calcula o momento de inércia transversal (I_T) da área do plano de flutuação.
        """
        # 1. Filtra as balizas que estão estritamente DENTRO da linha d'água
        x_internos = [x for x in self.casco.posicoes_balizas if x > self.x_re and x < self.x_vante]
        # Calcula a meia-boca ao cubo para estas balizas
        y_cubed_internas = [self.casco.obter_meia_boca(x, self.calado)**3 for x in x_internos]

        # 2. Lógica condicional para as extremidades
        baliza_popa_x = min(self.casco.posicoes_balizas)
        baliza_proa_x = max(self.casco.posicoes_balizas)
        tolerancia = 1e-3

        # Verifica a extremidade de ré
        if abs(self.x_re - baliza_popa_x) < tolerancia:
            # Se x_re coincide com a baliza de popa, usa a meia boca daquela baliza
            y_cubed_re = self.casco.obter_meia_boca(baliza_popa_x, self.calado)**3
        else:
            # Caso contrário, a meia boca na interseção é zero
            y_cubed_re = 0.0

        if abs(self.x_vante - baliza_proa_x) < tolerancia:
            # Se x_vante coincide com a baliza de proa, usa a meia boca daquela baliza
            y_cubed_vante = self.casco.obter_meia_boca(baliza_proa_x, self.calado)**3
        else:
            # Caso contrário, a meia boca na interseção é zero
            y_cubed_vante = 0.0

        # 3. Constrói a lista final de pontos para a interpolação da curva de y³
        x_pontos = [self.x_re] + x_internos + [self.x_vante]
        y_cubed_pontos = [y_cubed_re] + y_cubed_internas + [y_cubed_vante]
        
        # 4. Criação do Interpolador (y³ = f(x)) e Integração
        if len(x_pontos) < 2:
            self.momento_inercia_transversal = 0.0
            return

        pontos_unicos = sorted(list(set(zip(x_pontos, y_cubed_pontos))))
        x_pontos_unicos = [p[0] for p in pontos_unicos]
        y_cubed_pontos_unicos = [p[1] for p in pontos_unicos]

        if self.metodo_interp == 'pchip':
            interpolador_y3 = PchipInterpolator(x_pontos_unicos, y_cubed_pontos_unicos, extrapolate=False)
        else:
            interpolador_y3 = interp1d(x_pontos_unicos, y_cubed_pontos_unicos, kind='linear', bounds_error=False, fill_value=0.0)
        
        integral_y3, erro = quad(interpolador_y3, self.x_re, self.x_vante)
        
        # Fórmula: I_T = (2/3) * integral de y³ dx
        self.momento_inercia_transversal = (2/3) * integral_y3

    def _calcular_momento_inercia_longitudinal(self):
        """
        Calcula o momento de inércia longitudinal (I_L) da área do plano de flutuação
        em relação ao seu centroide (LCF).
        """
        # Verifica se os pré-requisitos para o cálculo existem
        if self.area_plano_flutuacao == 0.0 or not self.interpolador_wl or self.lcf is None:
            self.momento_inercia_longitudinal = 0.0
            return
            
        # 1. Define a função a ser integrada: (x - LCF)² * y(x)
        funcao_momento_inercia = lambda x: ((x - self.lcf)**2) * self.interpolador_wl(x)
        
        # 2. Integra para obter o momento de inércia da meia-área
        momento_meia_area, erro = quad(funcao_momento_inercia, self.x_re, self.x_vante)
        
        # 3. O momento de inércia total é o dobro do momento da meia-área
        self.momento_inercia_longitudinal = momento_meia_area * 2

    def _calcular_propriedades_derivadas(self):
        """
        Calcula as propriedades hidrostáticas finais que dependem dos valores base.
        """
        # --- Estabilidade Transversal ---
        if self.volume and self.volume > 1e-6:
            self.bmt = self.momento_inercia_transversal / self.volume
            self.kmt = self.vcb + self.bmt
        else:
            self.bmt = 0.0
            self.kmt = 0.0

        # --- Estabilidade Longitudinal ---
        if self.volume and self.volume > 1e-6:
            self.bml = self.momento_inercia_longitudinal / self.volume
            self.kml = self.vcb + self.bml
        else:
            self.bml = 0.0
            self.kml = 0.0

        # --- Outras Propriedades Hidrostáticas ---
        self.tpc = (self.area_plano_flutuacao * self.densidade) / 100.0
        
        if self.lwl and self.lwl > 1e-6:
            self.mtc = (self.momento_inercia_longitudinal * self.densidade) / (100 * self.lwl)
        else:
            self.mtc = 0.0
        
        # --- Coeficientes de Forma ---
        # Pré-requisitos
        volume_carena = self.volume if self.volume is not None else 0.0
        lwl = self.lwl if self.lwl is not None else 0.0
        bwl = self.bwl if self.bwl is not None else 0.0
        calado = self.calado
        awp = self.area_plano_flutuacao if self.area_plano_flutuacao is not None else 0.0
        
        # Encontra a área da seção mestra (Am) - a maior área de seção calculada
        area_secao_mestra = max(self.areas_secoes.values()) if self.areas_secoes else 0.0

        # Denominador do paralelepípedo circunscrito (Lwl * Bwl * T)
        denominador_bloco = lwl * bwl * calado
        self.cb = volume_carena / denominador_bloco if denominador_bloco > 1e-6 else 0.0

        # Denominador do prisma longitudinal (Am * Lwl)
        denominador_prismatico = area_secao_mestra * lwl
        self.cp = volume_carena / denominador_prismatico if denominador_prismatico > 1e-6 else 0.0
        
        # Denominador do retângulo do plano de flutuação (Lwl * Bwl)
        denominador_plano_flutuacao = lwl * bwl
        self.cwp = awp / denominador_plano_flutuacao if denominador_plano_flutuacao > 1e-6 else 0.0

        # Coeficiente de Seção Mestra (Cm)
        self.cm = self.cb / self.cp if self.cp > 1e-6 else 0.0

    def _calcular_todas_propriedades(self):
        """Método privado para chamar todos os outros cálculos na ordem correta."""
        print(f"\n--- Calculando propriedades para o calado T = {self.calado:.3f} m ---")
        
        # 1. Cálculos de Geometria e Áreas
        self._calcular_dimensoes_linha_dagua()
        self._calcular_area_plano_flutuacao()
        self._calcular_lcf()
        for x_pos in self.casco.posicoes_balizas:
            self.areas_secoes[x_pos] = self._calcular_area_secao(x_pos)
        
        # 2. Cálculos baseados em Volume
        # O cálculo de volume agora também cria o self.interpolador_areas
        self._calcular_volume_deslocamento()
        # Com o volume e o interpolador_areas prontos, podemos calcular o LCB
        self._calcular_lcb()
        # Com a Área de flutuação e o Volume, podemos calcular o VCB
        self._calcular_vcb()
        
        # O cálculo de I_T e I_L pode ser feito após a AWP e LCF serem conhecidos
        self._calcular_momento_inercia_transversal()
        self._calcular_momento_inercia_longitudinal()

        self._calcular_propriedades_derivadas()

def calcular_propriedades_para_um_calado(args):
    """
    Função "worker" que será executada em um processo separado.
    Ela recebe todos os dados necessários e retorna um dicionário de resultados.
    """
    casco, calado, densidade, metodo_interp = args
    
    # Cria o objeto de propriedades, que executa todos os cálculos para este calado
    props = PropriedadesHidrostaticas(casco, calado, densidade, metodo_interp)
    
    # Retorna um dicionário com os resultados
    return {
        'Calado (T)': calado,
        'Volume (∇)': props.volume, 'Desloc. (Δ)': props.deslocamento,
        'AWP': props.area_plano_flutuacao, 'LWL': props.lwl, 'BWL': props.bwl,
        'LCB': props.lcb, 'VCB (KB)': props.vcb, 'LCF': props.lcf,
        'IT': props.momento_inercia_transversal, 'IL': props.momento_inercia_longitudinal,
        'BMt': props.bmt, 'KMt': props.kmt, 'BMl': props.bml, 'KMl': props.kml,
        'TPC': props.tpc, 'MTc': props.mtc, 'Cb': props.cb, 'Cp': props.cp,
        'Cwp': props.cwp, 'Cm': props.cm,
    }

# ==============================================================================
# CALCULADORA HIDROSTÁTICA - ESCOLHA UMA DAS VERSÕES ABAIXO
# ==============================================================================

# --- VERSÃO 1: CÁLCULO SEQUENCIAL (COM CRONÔMETRO) ---
# class CalculadoraHidrostatica:
#     """
#     Versão sequencial (um calado de cada vez) para comparação.
#     """
#     def __init__(self, casco: Casco, densidade: float, metodo_interp: str):
#         self.casco = casco
#         self.densidade = densidade
#         self.metodo_interp = metodo_interp
        
#     def calcular_curvas(self, lista_de_calados: list) -> pd.DataFrame:
#         start_time = time.perf_counter() # Inicia o cronômetro
        
#         print(f"\nIniciando cálculo SEQUENCIAL das curvas para {len(lista_de_calados)} calados...")
#         lista_de_resultados = []
#         for calado in sorted(lista_de_calados):
#             if calado <= 0: continue
#             args = (self.casco, calado, self.densidade, self.metodo_interp)
#             resultado = calcular_propriedades_para_um_calado(args)
#             lista_de_resultados.append(resultado)
            
#         end_time = time.perf_counter() # Para o cronômetro
#         duration = end_time - start_time
#         print(f"Cálculo sequencial finalizado em {duration:.2f} segundos.")
        
#         return pd.DataFrame(lista_de_resultados)


# --- VERSÃO 2: CÁLCULO PARALELO (COM CRONÔMETRO) ---
class CalculadoraHidrostatica:
    """
    Versão paralela (multiprocessing) para máxima performance.
    """
    def __init__(self, casco: Casco, densidade: float, metodo_interp: str):
        self.casco = casco
        self.densidade = densidade
        self.metodo_interp = metodo_interp
        
    def calcular_curvas(self, lista_de_calados: list) -> pd.DataFrame:
        start_time = time.perf_counter() # Inicia o cronômetro
        
        print(f"\nIniciando cálculo PARALELO das curvas para {len(lista_de_calados)} calados...")
        
        tarefas = [(self.casco, calado, self.densidade, self.metodo_interp) for calado in sorted(lista_de_calados) if calado > 0]
        lista_de_resultados = []

        with concurrent.futures.ProcessPoolExecutor() as executor:
            lista_de_resultados = list(executor.map(calcular_propriedades_para_um_calado, tarefas))
            
        end_time = time.perf_counter() # Para o cronômetro
        duration = end_time - start_time
        print(f"Cálculo paralelo finalizado em {duration:.2f} segundos.")
        
        lista_de_resultados.sort(key=lambda r: r['Calado (T)'])
        return pd.DataFrame(lista_de_resultados)