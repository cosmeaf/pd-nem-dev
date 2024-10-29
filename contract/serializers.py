from rest_framework import serializers
from contract.models import EnemData, MeritoAcademico

class EnemDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemData
        fields = ['id', 'nome', 'cpf', 'nota_matematica', 'nota_redacao', 'nota_geral', 'created_at', 'updated_at']

class MeritoAcademicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritoAcademico
        fields = ['id', 'nome_aluno', 'nome_diretor', 'nome_escola', 'endereco_escola', 'data', 'media_ensino_medio', 'pdf_url', 'created_at', 'updated_at']
