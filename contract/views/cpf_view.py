import requests
from django.shortcuts import render, redirect
from decouple import config
from contract.forms import CPFForm
from contract.views.messages_view import render_message
import logging

logger = logging.getLogger('django')

# Carregar variáveis de ambiente com segurança
API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

def cpf_view(request):
    if request.method == 'POST':
        form = CPFForm(request.POST)
        if form.is_valid():
            # CPF já está validado e limpo pelo formulário
            cpf = form.cleaned_data['cpf']
            logger.info(f"CPF recebido via POST {cpf} CPF_VIEW")

            url = f'{API_BASE_URL}/form/cpf/{cpf}/'
            headers = {'api-key': API_KEY}

            try:
                # Requisição à API com timeout e tratamento de erro
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()  # Levanta exceção para códigos de status 4xx e 5xx

                try:
                    data = response.json()

                    # Valida se os campos esperados estão presentes na resposta
                    if 'id' not in data or 'cpf' not in data or 'applyMethod' not in data:
                        return render_message(request, 'error.html',
                                              title='Erro na Resposta da API',
                                              message='A resposta da API não contém os dados esperados.',
                                              code=500)
                    
                    # Salva os dados retornados na sessão, incluindo novos campos
                    request.session['user_id'] = data.get('id')
                    request.session['cpf'] = data.get('cpf')
                    request.session['apply_method'] = data.get('applyMethod')
                    request.session['cel'] = data.get('cel')  # Novo campo salvo na sessão
                    request.session['cel_responsavel'] = data.get('celResponsavel')  # Novo campo salvo na sessão
                    request.session['email'] = data.get('email')  # Novo campo salvo na sessão

                    # Redireciona com base no método de aplicação
                    if data.get('applyMethod') == 'Enem':
                        return redirect('enem_upload')
                    elif data.get('applyMethod') == 'MeritoAcademico':
                        return redirect('merito_academico_input')

                except ValueError:
                    # Captura erro de conversão de JSON
                    return render_message(request, 'error.html', 
                                          title='Erro de JSON',
                                          message='A resposta da API retornou um JSON inválido.',
                                          code=500,
                                          error=response.text)
            except requests.exceptions.HTTPError as http_err:
                # Captura erros HTTP (ex.: 4xx, 5xx)
                logger.error(f"Erro HTTP: {http_err}")
                return render_message(request, 'error.html', 
                                      title='Erro na API',
                                      message=f'Erro na comunicação com a API: {response.status_code}.',
                                      code=response.status_code,
                                      error=str(http_err))
            except requests.exceptions.RequestException as e:
                # Captura erros de conexão
                logger.error(f"Erro de conexão: {e}")
                return render_message(request, 'error.html', 
                                      title='Erro de Conexão',
                                      message='Erro de conexão com a API. Por favor, tente novamente mais tarde.',
                                      code=503,
                                      error=str(e))
    else:
        form = CPFForm()

    return render(request, 'cpf_form.html', {'form': form})
