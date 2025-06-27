from rest_framework import serializers
from .models import Succulent, Pot

class SucculentSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Succulent
        fields = ['id', 'name', 'price', 'description', 'image_path']

    def get_image_path(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)


class PotSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Pot
        fields = ['id', 'name', 'material', 'height', 'width', 'price', 'description', 'image_path']

    def get_image_path(self, obj):
        return self.context['request'].build_absolute_uri(obj.image.url)

