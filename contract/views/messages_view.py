from django.shortcuts import render

# View para mensagens de sucesso
def confirm_success_view(request):
    message = 'Dados enviados com sucesso!'
    return render(request, 'confirm_success.html', {'message': message})

# View para mensagens de erro
def confirm_error_view(request):
    message = 'Ocorreu um erro ao tentar enviar os dados. Por favor, tente novamente mais tarde.'
    return render(request, 'confirm_error.html', {'message': message})



def render_message(request, message_type, **kwargs):
    """
    View genérica para lidar com diferentes tipos de mensagens (sucesso, erro, etc.).
    """
    messages = {
        'success': {
            'title': 'Sucesso',
            'message': 'Seus dados foram enviados com sucesso e estão sendo processados.',
            'template': 'message.html'
        },
        'error': {
            'title': 'Erro',
            'message': 'Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.',
            'template': 'message.html'
        },
        'info': {
            'title': 'Informação',
            'message': 'Aqui está uma mensagem informativa.',
            'template': 'message.html'
        },
        'warning': {
            'title': 'Atenção',
            'message': 'Há algo que você precisa verificar antes de continuar.',
            'template': 'message.html'
        },
        'alert': {
            'title': 'Alerta',
            'message': 'Algo inesperado aconteceu. Por favor, tome as devidas precauções.',
            'template': 'message.html'
        }
    }

    # Selecionar os detalhes da mensagem com base no tipo fornecido
    message_details = messages.get(message_type, {
        'title': 'Mensagem',
        'message': 'Tipo de mensagem não identificado.',
        'template': 'message.html'
    })

    # Atualizar o dicionário com os argumentos fornecidos
    context = {
        'title': kwargs.get('title', message_details['title']),
        'message': kwargs.get('message', message_details['message']),
        'message_type': f'message-{message_type}',  # Incluindo message_type no contexto
    }

    # Renderizar o template com os dados atualizados
    return render(request, message_details['template'], context)
