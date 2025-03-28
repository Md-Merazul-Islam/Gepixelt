# serializers.py
from rest_framework import serializers
from .models import Product, WeeklyOrder, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity','price', ]
        read_only_fields = ['price']


class WeeklyOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = WeeklyOrder
        fields = ['day_of_week', 'number_of_people', 'order_items']
