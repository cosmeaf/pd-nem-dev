from rest_framework import serializers
from contract.models import EnemData, MeritoAcademico

class EnemDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnemData
        fields = '__all__'
        
class MeritoAcademicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeritoAcademico
        fields = '__all__'
