class Header extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
        <header>
            <div class="imagem_cabecalho">
                <img src="/imagens/logo_header.png" alt="Logo da empresa Condo Secure">
            </div>
            <nav class="nav-menu">
                <div class="nav-group-left">
                    <div class="dropdown">
                        <button class="dropdown-btn">
                            <img src="/imagens/icone_calendario.png" alt="Ícone de Calendário">
                            <span>Agendamentos</span>
                            <i class="fa-solid fa-chevron-down"></i>
                        </button>
                        <div class="dropdown-content">
                            <a href="p_agend_salaoF.html">Salão de Festas</a>
                            <a href="p_agend_churrasqueira.html">Churrasqueira</a>
                        </div>
                    </div>
                    <span class="separator">/</span>
                    <div class="usuario">
                        <div class="icone_usuario">
                            <img src="/imagens/icone_usuario.png" alt="Ícone de Usuário">
                        </div>
                        <p class="nomeUsuario">João Gilberto</p>
                        <div class="icone_sair">
                            <img src="/imagens/icone_sair.png" alt="Ícone para sair da Página">
                        </div>
                    </div>
                </div>
            </nav>
        </header>
        `;

        // Pega o botão e o conteúdo do dropdown
        const dropdownBtn = document.querySelector('.dropdown-btn');
        const dropdownContent = document.querySelector('.dropdown-content');

        // Adiciona um "escutador de evento" que espera por um clique no botão
        dropdownBtn.addEventListener('click', function() {
          // A cada clique, ele adiciona ou remove a classe 'show' do conteúdo
        dropdownContent.classList.toggle('show');
        });

        // Opcional: Fecha o dropdown se o usuário clicar fora dele
        window.addEventListener('click', function(event) {
          // Verifica se o clique NÃO foi no botão
        if (!dropdownBtn.contains(event.target)) {
            // Se o menu estiver aberto, fecha ele
            if (dropdownContent.classList.contains('show')) {
            dropdownContent.classList.remove('show');
            }
        }
        });

    }
}

customElements.define('main-header', Header);