
          #Rota para o Recaptcha Google 
import os
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

# Carregue a variável de ambiente (instale python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()

RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

@app.route('/')
def index():
   return render_template('cad_con_churrasqueira.html')

@app.route('/seu-formulario', methods=['GET', 'POST'])
def handle_form():
    if request.method == 'POST':
        # Recebe o token do reCAPTCHA do formulário
        recaptcha_response = request.form.get('g-recaptcha-response')

        if recaptcha_response:
            # Dados para enviar ao Google para validação
            data = {
                'secret': RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }

            # Faz a requisição de validação para a API do Google
            response = requests.post(GOOGLE_RECAPTCHA_VERIFY_URL, data=data)
            result = response.json()

            if result.get('success'):
                # Validação bem-sucedida! Continue o processo
                return "Formulário enviado com sucesso e reCAPTCHA verificado!"
            else:
                # Falha na validação do reCAPTCHA
                return "Erro na validação do reCAPTCHA. Tente novamente."

        return "Token reCAPTCHA não recebido."

    return render_template('seu_formulario.html') # Renderiza o formulário

if __name__ == '__main__':
    app.run(debug=True)

    #Fim da rota Recaptcha Google 