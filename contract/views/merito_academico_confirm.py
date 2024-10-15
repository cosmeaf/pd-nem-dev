import os
import requests
from django.shortcuts import render, redirect
from contract.utility.docx_utility import manipular_docx
from decouple import config
from contract.views.messages_view import confirm_error_view, confirm_success_view

API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

def merito_academico_confirm(request):
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao')

        if confirmacao == 'sim':
            # Coletar os dados da sessão
            nome_aluno = request.session.get('nome_aluno')
            nome_diretor = request.session.get('nome_diretor')
            nome_escola = request.session.get('nome_escola')
            endereco_escola = request.session.get('endereco_escola') 
            data = request.session.get('data')
            media_ensino_medio = request.session.get('media_ensino_medio')

            # Manipular o DOCX e gerar o arquivo PDF
            pdf_path = manipular_docx(nome_aluno, nome_diretor, nome_escola, endereco_escola, data, media_ensino_medio)

            # Obter o caminho da URL pública do arquivo gerado
            pdf_url = f'/media/documents/{os.path.basename(pdf_path)}'

            # Obter o user_id salvo na sessão
            user_id = request.session.get('user_id')

            # Enviar os dados via API
            url_method = f'{API_BASE_URL}/form/{user_id}/applyMethod'
            headers = {'api-key': API_KEY}
            body = {
                "applyMethod": "MeritoAcademico",
                "applyMethodGrade": media_ensino_medio,
            }

            try:
                response_method = requests.patch(url_method, headers=headers, json=body)
                response_method.raise_for_status()

                # Se o envio for bem-sucedido, exibir o PDF gerado
                return render(request, 'merito_academico_view_doc.html', {
                    'pdf_url': pdf_url,
                    'nome_aluno': nome_aluno
                })
            except requests.exceptions.RequestException as e:
                # Redirecionar para a página de erro
                return confirm_error_view(request, message=f"Erro ao enviar dados: {str(e)}")

        else:
            return redirect('merito_academico_input')

    # Carregar os dados da sessão para exibir na tela
    context = {
        'nome_aluno': request.session.get('nome_aluno'),
        'nome_diretor': request.session.get('nome_diretor'),
        'nome_escola': request.session.get('nome_escola'),
        'endereco_escola': request.session.get('endereco_escola'),
        'data': request.session.get('data'),
        'media_ensino_medio': request.session.get('media_ensino_medio'),
    }

    return render(request, 'merito_academico_confirm.html', context)
