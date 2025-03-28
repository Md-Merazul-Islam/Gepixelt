# serializers.py
from rest_framework import serializers
from .models import Product, WeeklyOrder, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'total_price']
        read_only_fields = ['price']
    def get_total_price(self, obj):
        return obj.total_price()


class WeeklyOrderSerializer(serializers.ModelSerializer):
    # Use 'order_items_week' to refer to the related name defined in the model
    order_items = OrderItemSerializer(source='order_items_week', many=True)

    class Meta:
        model = WeeklyOrder
        fields = ['day_of_week','total_amount', 'number_of_people', 'order_items']




class WeeklyOrderListSerializer(serializers.ModelSerializer):
    # Use 'order_items_week' for the related name in the WeeklyOrder model
    order_items = OrderItemSerializer(source='order_items_week', many=True)
    
    # Include customer information fields
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField()
    customer_address = serializers.CharField()
    customer_postal_code = serializers.CharField()
    stripe_payment_id = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = WeeklyOrder
        fields = ['id','day_of_week', 'number_of_people', 'order_items', 
                  'customer_name', 'customer_email', 'customer_phone',
                  'customer_address', 'customer_postal_code', 'stripe_payment_id', 'total_amount']

