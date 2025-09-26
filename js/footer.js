class Footer extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <footer class="footer">
            <div class="footer-allconteudo">
                <div class="footer-allvertical">
                    <div class="footer-msglogo">
                        <img src="/imagens/logo_rodape.png" class="footer-logo-icon" alt="Logotipo Rodapé">
                    </div>
                    <div>
                        <h3 class="footer-contato">Contato</h3>
                        <ul class="footer-contatos">
                            <li><p>grupopiunivespsala6grupo07.com</p></li>
                            <li><p>(11) 707070-7070</p></li>
                        </ul>
                    </div>
                    <div>
                        <h3 class="footer-localizacao">Localização</h3>
                        <p class="footer-endereco">
                            Rua Exemplo, 123<br>
                            Bairro Fictício, São Paulo - SP<br>
                            CEP: 01234-567
                        </p>
                    </div>
                </div>
            </div>
        </footer>
        `;
    }
}

customElements.define('main-footer', Footer);