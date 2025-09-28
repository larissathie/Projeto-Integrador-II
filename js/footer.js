class Footer extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <footer>
                <div class="rodape">
                    <div class="imagem_rodape">
                        <img src="/imagens/logo_rodape.png" alt="Logo da empresa Condo Secure">
                    </div>
                    <div class="dados_rodape">
                        <div class="email_rodape">
                            <h3>Email</h3>
                            <p>email@univesp.com.br</p>
                        </div>
                        <div class="localizacao_rodape">
                            <p>Localização</p>
                            <iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1139.5589665586933!2d-46.66968980722495!3d-23.493745474903747!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94cef78887c5c665%3A0x4b758544ce147597!2sRua%20Jos%C3%A9%20Soriano%20de%20Sousa%2C%20292%20-%20Casa%20Verde%20Alta%2C%20S%C3%A3o%20Paulo%20-%20SP%2C%2002555-050!5e1!3m2!1spt-BR!2sbr!4v1758844960400!5m2!1spt-BR!2sbr" width="auto" height="80" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
                        </div>
                    </div>
                </div>
            </footer>
        `;
    }
}

customElements.define('main-footer', Footer);