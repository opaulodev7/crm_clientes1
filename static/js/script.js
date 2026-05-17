// =========================
// CONFIRMAÇÃO EXCLUSÃO
// =========================

const deleteButtons = document.querySelectorAll('.btn-delete');

deleteButtons.forEach(button => {

    button.addEventListener('click', function(event) {

        const confirmar = confirm(
            'Deseja realmente excluir este registro?'
        );

        if (!confirmar) {
            event.preventDefault();
        }

    });

});


// =========================
// MODAL EDITAR CLIENTE
// =========================

const modalCliente = document.getElementById(
    'modalEditarCliente'
);

if (modalCliente) {

    const modalEditarCliente = new bootstrap.Modal(
        modalCliente
    );

    const botoesEditarCliente = document.querySelectorAll(
        '.btn-editar-cliente'
    );

    botoesEditarCliente.forEach(button => {

        button.addEventListener('click', () => {

            const id = button.dataset.id;

            document.getElementById(
                'editClienteId'
            ).value = id;

            document.getElementById(
                'editNome'
            ).value = button.dataset.nome || '';

            document.getElementById(
                'editTelefone'
            ).value = button.dataset.telefone || '';

            document.getElementById(
                'editEmail'
            ).value = button.dataset.email || '';

            document.getElementById(
                'editCidade'
            ).value = button.dataset.cidade || '';

            document.getElementById(
                'formEditarCliente'
            ).action = `/clientes/editar/${id}`;

            modalEditarCliente.show();

        });

    });

}


// =========================
// MODAL EDITAR SERVIÇO
// =========================

const modalServico = document.getElementById(
    'modalEditarServico'
);

if (modalServico) {

    const modalEditarServico = new bootstrap.Modal(
        modalServico
    );

    const botoesEditarServico = document.querySelectorAll(
        '.btn-editar-servico'
    );

    botoesEditarServico.forEach(button => {

        button.addEventListener('click', () => {

            const id = button.dataset.id;

            document.getElementById(
                'editServicoId'
            ).value = id;

            document.getElementById(
                'editServicoNome'
            ).value = button.dataset.nome || '';

            document.getElementById(
                'editServicoDescricao'
            ).value = button.dataset.descricao || '';

            document.getElementById(
                'editServicoValor'
            ).value = button.dataset.valor || '';

            document.getElementById(
                'editServicoData'
            ).value = formatarDataInput(
                button.dataset.data
            );

            document.getElementById(
                'editServicoCliente'
            ).value = button.dataset.cliente || '';

            document.getElementById(
                'formEditarServico'
            ).action = `/servicos/editar/${id}`;

            modalEditarServico.show();

        });

    });

}


// =========================
// FORMATAR DATA
// =========================

function formatarDataInput(data) {

    if (!data) return '';

    return data.substring(0, 10);

}


// =========================
// ANIMAÇÃO SUAVE TABELAS
// =========================

const linhasTabela = document.querySelectorAll(
    'tbody tr'
);

linhasTabela.forEach((linha, index) => {

    linha.style.opacity = '0';
    linha.style.transform = 'translateY(10px)';

    setTimeout(() => {

        linha.style.transition = '0.3s ease';

        linha.style.opacity = '1';
        linha.style.transform = 'translateY(0px)';

    }, index * 50);

});


// =========================
// GRÁFICO DASHBOARD
// =========================

const grafico = document.getElementById(
    'graficoServicos'
);

if (
    grafico &&
    typeof labels !== 'undefined'
) {

    new Chart(grafico, {

        type: 'bar',

        data: {

            labels: labels,

            datasets: [{

                label: 'Faturamento',

                data: valores,

                borderWidth: 1,

                borderRadius: 8

            }]

        },

        options: {

            responsive: true,

            plugins: {

                legend: {
                    display: true
                }

            },

            scales: {

                y: {
                    beginAtZero: true
                }

            }

        }

    });

}