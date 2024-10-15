from django.shortcuts import render

def session_view(request):
    # Obtém todos os dados da sessão como dicionário
    session_data = dict(request.session.items())

    return render(request, 'session_view.html', {
        'session_data': session_data
    })
