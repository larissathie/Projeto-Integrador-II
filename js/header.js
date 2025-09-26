class Header extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <header>
                <div class="logo-icone">
                    <img src="/imagens/logo_header.png" alt="Logotipo - Página Inicial">
                </div>
                <nav class="navegacao-menu">
                    <div class="navegacao-grupo-esquerda">
                        <div class="menu-suspenso">
                            <button class="botao-menu-suspenso">
                                <img src="/imagens/icone_calendario.png" alt="Ícone de Calendário">
                                <span>Agendamentos</span>
                                <i class="fa-solid fa-chevron-down"></i>
                            </button>
                            <div class="conteudo-menu-suspenso">
                                <a href="/agendamento-novo">Fazer novo agendamento</a>
                                <a href="/agendamentos-meus">Meus agendamentos</a>
                            </div>
                        </div>
                        <span class="separador">/</span>
                        <span class="link-navegacao link-usuario">
                            <img src="/imagens/icone_usuario.png" alt="Ícone do usuário">
                            João Gilberto
                        </span>
                    </div>
                    <a href="#" class="link-navegacao">
                        <img src="/imagens/icone_sair.png" alt="Ícone de Sair">
                    </a>
                </nav>
            </header>
        `;
    }
}

customElements.define('main-header', Header);