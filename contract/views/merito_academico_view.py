from django.shortcuts import render, redirect
from contract.forms import MeritoAcademicoForm


def merito_academico_input(request):
    if request.method == 'POST':
        form = MeritoAcademicoForm(request.POST)
        if form.is_valid():
            # Salvar os dados inseridos pelo usuário
            nome_aluno = form.cleaned_data['nome_aluno']
            nome_diretor = form.cleaned_data['nome_diretor']
            nome_escola = form.cleaned_data['nome_escola']
            endereco_escola = form.cleaned_data['endereco_escola']  # Novo campo de endereço
            data = form.cleaned_data['data']
            media_ensino_medio = form.cleaned_data['media_ensino_medio']

            # Salvar os dados na sessão para a próxima etapa
            request.session['nome_aluno'] = nome_aluno
            request.session['nome_diretor'] = nome_diretor
            request.session['nome_escola'] = nome_escola
            request.session['endereco_escola'] = endereco_escola  # Salvar endereço na sessão
            request.session['data'] = str(data)  # Salva como string
            request.session['media_ensino_medio'] = str(media_ensino_medio)

            # Redirecionar para confirmação
            return redirect('merito_academico_confirm')

    else:
        form = MeritoAcademicoForm()

    return render(request, 'merito_academico_input.html', {'form': form})