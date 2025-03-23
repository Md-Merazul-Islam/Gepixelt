from rest_framework import serializers
from .models import Card, CardItem, Product

class CardItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = CardItem
        fields = ['id', 'product', 'product_name', 'quantity', 'total_price']

class CardSerializer(serializers.ModelSerializer):
    items = CardItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Card
        fields = ['id', 'user', 'items', 'total_price']
        read_only_fields = ['user']
