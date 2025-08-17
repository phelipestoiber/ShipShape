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

});