from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        read_only_fields = ['price']
    # def validate(self, data):
    #     # Ensure price is valid for the product
    #     product = data.get('product')
    #     if product and not product.price:
    #         raise serializers.ValidationError("Product price is missing.")
    #     data['price'] = product.price  # Set the price explicitly
    #     return data

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date',
                  'receive_date', 'total_price', 'status', 'items']
        read_only_fields = ['total_price']

    # # def validate(self, data):
    # #     # Access the user from the request context
    # #     user = self.context['request'].user
    # #     items = data.get('items', [])

    # #     total_price = 0
    # #     for item in items:
    # #         product = item.get('product')
    # #         if not isinstance(product, Product):
    # #             raise serializers.ValidationError("Invalid product reference.")
    # #         total_price += product.price * item.get('quantity', 1)

    # #     if user.balance < total_price:
    # #         raise serializers.ValidationError(
    # #             "You don't have enough balance to place this order.")

    #     return data

    # def create(self, validated_data):
    #     items_data = validated_data.pop('items', [])
    #     user = self.context['request'].user
    #     validated_data.pop('user', None)  # Remove 'user' from validated_data
        
    #     total_price = 0  # Initialize total price variable
    #     for item in items_data:
    #         product = item['product']
    #         total_price += product.price * item['quantity']  # Calculate total price for all items

    #     # Check if the user has enough balance
    #     if user.balance < total_price:
    #         raise serializers.ValidationError("Insufficient balance to place this order.")

    #     # Create the order and save total_price
    #     order = Order.objects.create(**validated_data, user=user, total_price=total_price)

    #     # Create order items
    #     for item_data in items_data:
    #         OrderItem.objects.create(order=order, **item_data)

    #     return order

    # def handle_validation_error(self, exc):
    #     # Override to catch validation error and format it correctly
    #     raise serializers.ValidationError({
    #         "success": False,
    #         "statusCode": 400,
    #         "message": "Order creation failed",
    #         "error": {
    #             "message": str(exc)  # Directly show the error message
    #         }
    #     })


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['status']
