from rest_framework import serializers
from .models import Order, OrderItem, Product


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date',
                  'receive_date', 'total_price', 'status', 'items']
        read_only_fields = ['total_price']

    def validate(self, data):
        user = self.context['request'].user
        items = data.get('items', [])

        total_price = 0
        for item in items:
            product = item.get('product')  # Fetch product instance
            if not isinstance(product, Product):
                raise serializers.ValidationError("Invalid product reference.")
            total_price += product.price * item.get('quantity', 1)

        if user.balance < total_price:
            raise serializers.ValidationError(
                "You don't have enough balance to place this order."
            )

        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user  # Ensure the user is correctly assigned

        total_price = 0
        for item in items_data:
            product = item['product']
            total_price += product.price * item['quantity']

        if user.balance < total_price:
            raise serializers.ValidationError("Insufficient balance to place this order.")

        # Deduct balance from user
        user.balance -= total_price
        user.save(update_fields=['balance'])

        # Create order (ensure user is passed separately)
        order = Order.objects.create(**validated_data)

        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
