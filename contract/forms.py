from django import forms
from django.core.exceptions import ValidationError
from contract.utility.cpf_validate import CPFValidator
from datetime import date
import logging

logger = logging.getLogger('django')

MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_file_size(file):
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(f"O tamanho do arquivo não pode exceder {MAX_FILE_SIZE / (1024 * 1024)} MB.")

    
class CPFForm(forms.Form):
    cpf = forms.CharField(
        max_length=14,
        label="CPF",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu CPF'})
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')

        # Remover qualquer formatação anterior (pontos e traços)
        cpf_limpo = cpf.replace('.', '').replace('-', '')

        # Inicializar o CPFValidator com o CPF limpo
        validator = CPFValidator(cpf_limpo)

        # Verificar se o CPF é válido
        if not validator.is_valid():
            raise forms.ValidationError("CPF inválido.")
        
        # Em vez de retornar o CPF formatado, retornar o CPF "limpo" (sem formatação)
        return cpf_limpo  # Agora o CPF será retornado sem pontos ou traços


class EnemPDFUploadForm(forms.Form):
    pdf_file = forms.FileField(
        label="Upload do PDF do ENEM",
        required=True,
        validators=[validate_file_size],  # Validação de tamanho adicionada
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf'})
    )

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Verificar se a extensão do arquivo é .pdf
            if not pdf_file.name.lower().endswith('.pdf'):
                logger.info(f"Extensão do arquivo inválida: {pdf_file.name}")
                raise forms.ValidationError("Apenas arquivos no formato PDF são permitidos. Por favor, baixe o arquivo oficial do site do ENEM.")

            # Verificar o tipo MIME do arquivo
            if pdf_file.content_type != 'application/pdf':
                logger.info(f"Tipo MIME inválido: {pdf_file.content_type}")
                raise forms.ValidationError("O arquivo enviado não é um PDF válido.")
        
        logger.info("Arquivo PDF válido.")
        return pdf_file
    
    

class MeritoAcademicoForm(forms.Form):
    nome_aluno = forms.CharField(
        label='Nome do Aluno',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do aluno'})
    )
    nome_diretor = forms.CharField(
        label='Nome do Diretor',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome do diretor'})
    )
    nome_escola = forms.CharField(
        label='Nome da Escola',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da escola'})
    )
    endereco_escola = forms.CharField(
        label='Endereço Completo da Escola',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o endereço completo da escola'})
    )
    data = forms.DateField(
        label='Data',
        initial=date.today().strftime('%d/%m/%Y'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )
    media_ensino_medio = forms.DecimalField(
        label='Média do Ensino Médio',
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Digite a média final'})
    )

    def clean_media_ensino_medio(self):
        media = self.cleaned_data.get('media_ensino_medio')
        if media < 0 or media > 10:
            raise forms.ValidationError("A média deve ser entre 0.00 e 10.00.")
        return media
