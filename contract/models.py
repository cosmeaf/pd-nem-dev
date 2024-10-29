from django.db import models
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

class EnemData(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    nota_matematica = models.DecimalField(max_digits=5, decimal_places=2)
    nota_redacao = models.DecimalField(max_digits=5, decimal_places=2)
    nota_geral = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        try:
            self.nota_matematica = Decimal(str(self.nota_matematica).replace(',', '.'))
            self.nota_redacao = Decimal(str(self.nota_redacao).replace(',', '.'))
            self.nota_geral = Decimal(str(self.nota_geral).replace(',', '.'))
        except InvalidOperation:
            raise ValueError("Erro na conversão das notas para o formato decimal.")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nome} - {self.cpf}'



class MeritoAcademico(models.Model):
    nome_aluno = models.CharField(max_length=255)
    nome_diretor = models.CharField(max_length=255)
    nome_escola = models.CharField(max_length=255)
    endereco_escola = models.CharField(max_length=255)
    data = models.CharField(max_length=10)  # Altere para CharField
    media_ensino_medio = models.DecimalField(max_digits=4, decimal_places=2)
    pdf_url = models.CharField(max_length=255, blank=True, null=True)
    cpf = models.CharField(max_length=11, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nome_aluno} - {self.nome_escola}'