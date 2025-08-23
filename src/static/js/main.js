// Este evento garante que o script só será executado depois que todo o HTML for carregado.
document.addEventListener('DOMContentLoaded', function() {

    // ==========================================
    // === LÓGICA DA SIDEBAR RETRÁTIL =========
    // ==========================================
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const appLayout = document.querySelector('.app-layout');

    if (sidebarToggle && appLayout) {
        sidebarToggle.addEventListener('click', function() {
            appLayout.classList.toggle('sidebar-collapsed');
        });
    }


    // ==================================================
    // === LÓGICA DO FORMULÁRIO HIDROSTÁTICO ==========
    // ==================================================
    
    // Tenta encontrar os radio buttons do formulário hidrostático
    const calcMethodRadios = document.querySelectorAll('input[name="calc_method"]');
    
    // Se os radio buttons existirem nesta página...
    if (calcMethodRadios.length > 0) {
        const numCaladosInput = document.querySelector('input[name="num_calados"]');
        const incCaladosInput = document.querySelector('input[name="inc_calados"]');
        const listaCaladosInput = document.querySelector('input[name="lista_calados"]');

        // Função para atualizar o estado dos campos de texto
        function updateInputsState() {
            const selectedMethod = document.querySelector('input[name="calc_method"]:checked').value;

            // Desabilita todos por padrão, para garantir um estado limpo
            numCaladosInput.disabled = true;
            incCaladosInput.disabled = true;
            listaCaladosInput.disabled = true;

            // Habilita apenas o campo correspondente à opção de rádio selecionada
            if (selectedMethod === 'numero') {
                numCaladosInput.disabled = false;
            } else if (selectedMethod === 'incremento') {
                incCaladosInput.disabled = false;
            } else if (selectedMethod === 'manual') {
                listaCaladosInput.disabled = false;
            }
        }

        // Adiciona um "escutador" para cada radio button que chama a função de atualização
        calcMethodRadios.forEach(radio => {
            radio.addEventListener('change', updateInputsState);
        });

        // Executa a função uma vez no carregamento da página para definir o estado inicial correto
        updateInputsState();
    }

    // ===============================================
    // === LÓGICA DA TABELA DE RESULTADOS (DATATABLES)
    // ===============================================
    
    // Procura por uma tabela com o ID que definimos
    if ($('#tabela-resultados').length) {
        console.log("Tabela de resultados encontrada. Inicializando DataTables.");
        
        // Ativa o DataTables na nossa tabela
        $('#tabela-resultados').DataTable({
            "pageLength": 10, // Define o número de linhas por página
            "searching": false, // Desabilita barra de busca
            "language": {     // Traduz a interface para o português
                "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
            }
        });
    }

    // ==========================================================
    // === LÓGICA DE FEEDBACK DE CARREGAMENTO (LOADING) =======
    // ==========================================================

    // Tenta encontrar o formulário de cálculo pelo ID que adicionamos
    const hydroForm = document.getElementById('calculation-form');

    if (hydroForm) {
        // Adiciona um "escutador" para o evento de SUBMISSÃO do formulário
        hydroForm.addEventListener('submit', function() {
            // Quando o formulário for enviado, exibe o pop-up de carregamento
            Swal.fire({
                title: 'Calculando...',
                html: 'Por favor, aguarde enquanto os resultados são processados.',
                // Impede que o usuário feche o pop-up clicando fora
                allowOutsideClick: false, 
                // Mostra a animação de "carregando"
                didOpen: () => {
                    Swal.showLoading();
                }
            });
        });
    }

});