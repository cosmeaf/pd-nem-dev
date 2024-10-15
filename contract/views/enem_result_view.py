from django.shortcuts import render
import logging

logger = logging.getLogger('django')

# View para exibir os resultados
def enem_result_view(request):
    # Recuperar os dados da sessão
    nome = request.session.get('nome', '')
    cpf_extraido = request.session.get('cpf_extraido', '')
    nota_matematica = request.session.get('nota_matematica', '')
    nota_redacao = request.session.get('nota_redacao', '')
    nota_geral = request.session.get('nota_geral', '')

    # Debug: imprimir os valores recuperados da sessão
    logger.info(f"Nome: {nome}")
    logger.info(f"CPF extraído: {cpf_extraido}")
    logger.info(f"Nota de Matemática: {nota_matematica}")
    logger.info(f"Nota de Redação: {nota_redacao}")
    logger.info(f"Nota Geral: {nota_geral}")

    # Exibir os dados e pedir confirmação
    return render(request, 'enem_result.html', {
        'nome': nome,
        'cpf_extraido': cpf_extraido,
        'nota_matematica': nota_matematica,
        'nota_redacao': nota_redacao,
        'nota_geral': nota_geral,
        'confirm_message': 'Os dados estão corretos? Se sim, confirme o envio, ou entre em contato com o suporte.'
    })
