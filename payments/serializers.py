from .models import Order, Product, OrderProduct
from .models import OrderProduct, Product
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Subscription
from rest_framework import serializers
from .models import Order
from datetime import date


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'product', 'quantity', 'order_date', 'postal_code',
                  'address', 'email', 'phone_number', 'city', 'total_price']

    def create(self, validated_data):
        # Calculate total price
        validated_data['total_price'] = validated_data['product'].price_per_item * \
            validated_data['quantity']
        # Automatically set the order date to today's date
        validated_data['order_date'] = date.today()
        order = Order.objects.create(**validated_data)
        return order


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['customer', 'plan_type', 'price', 'start_date', 'end_date']

    def create(self, validated_data):
        # Subscription for weekly plan
        plan_type = validated_data.get('plan_type', 'weekly')
        price = validated_data.get('price', 20.00)  # Set default weekly price
        start_date = timezone.now().date()
        # Weekly subscription ends in 1 week
        end_date = start_date + timedelta(weeks=1)
        subscription = Subscription.objects.create(
            customer=validated_data['customer'],
            plan_type=plan_type,
            price=price,
            start_date=start_date,
            end_date=end_date
        )
        return subscription


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price_per_item']

        from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['customer', 'products', 'postal_code', 'address',
                  'email', 'phone_number', 'city', 'total_price']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        total_price = Decimal(0.0)

        # Add the products and their quantities to the order, and calculate the total price
        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price_per_item = product.price_per_item
            total_price += price_per_item * quantity

            # Create an OrderProduct entry for each product in the order
            order_product = OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_per_item=price_per_item
            )

        # Update the order's total price
        order.total_price = total_price
        order.save()

        return order
