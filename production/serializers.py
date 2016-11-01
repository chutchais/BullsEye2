from rest_framework import serializers
from .models import Bom


class BomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bom
        fields = ('name', 'model', 'rev')