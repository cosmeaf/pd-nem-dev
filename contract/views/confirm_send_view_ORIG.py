import requests
from django.shortcuts import redirect
from decouple import config  # Importa o config para carregar as variáveis de ambiente
from django.urls import reverse

# Carregar URL base da API e chave de API do arquivo .env
API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

# View para enviar os dados para a API usando PATCH
def confirm_send_view(request):
    if request.method == 'POST':
        # Obter os dados da sessão
        id_value = request.session.get('user_id')
        nota_geral = request.session.get('nota_geral')
        apply_method = request.session.get('apply_method')
        print(f"Id User: {id_value}")
        print(f"Nota Geral: {nota_geral}")
        print(f"Metodo: {apply_method}")

        # URL do endpoint dinâmico usando a variável API_BASE_URL
        url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'

        # Headers da API
        headers = {
            'api-key': API_KEY
        }

        # Body da requisição (enviado em formato JSON)
        body = {
            "applyMethod": apply_method,
            "applyMethodGrade": nota_geral,
        }

        # Enviar os dados para a API com o método PATCH
        try:
            response_method = requests.patch(url_method, headers=headers, json=body)
            response_method.raise_for_status()  # Levanta uma exceção para status de erro

            # Limpar a sessão em caso de sucesso
            request.session.flush()

            # Redirecionar para a view de sucesso
            return redirect('confirm_success')

        except requests.exceptions.RequestException as e:
            # Redirecionar para a view de erro em caso de exceção
            return redirect('confirm_error')

    # Se o método da requisição não for POST, redirecionar para a página de resultados
    return redirect('enem_result')
