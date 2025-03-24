# serializers.py

from rest_framework import serializers
from .models import Order, OrderProduct, Product, SubscriptionPlan, UserSubscription
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']  # Add any other fields you want to expose


# OrderProduct Serializer (many-to-many relationship between Order and Product)
class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price_per_item']  # Fields to include in the OrderProduct


# Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)  # Many-to-many relation for products
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order_date = serializers.DateField()  # User inputs the order date

    class Meta:
        model = Order
        fields = ['id', 'customer', 'products', 'order_date', 'total_price', 'create_date']

    def create(self, validated_data):
        # Extract product data from the validated data
        products_data = validated_data.pop('products')

        # Automatically set the create_date to today's date
        validated_data['create_date'] = timezone.now().date()

        # Create the Order instance
        order = Order.objects.create(total_price=0, **validated_data)  # Temporary total price

        # Calculate the total price and save the order
        total_price = Decimal(0)
        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price_per_item = product.price
            total_price += price_per_item * quantity

            # Create OrderProduct instance
            OrderProduct.objects.create(order=order, product=product, quantity=quantity, price_per_item=price_per_item)

        order.total_price = total_price
        order.save()  # Save the updated total_price to the order

        return order


# SubscriptionPlan Serializer
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration_days', 'price']


# UserSubscription Serializer
class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer()

    class Meta:
        model = UserSubscription
        fields = ['user', 'plan', 'balance', 'start_date', 'end_date']

    def update(self, instance, validated_data):
        # Update user subscription balance or other details
        plan_data = validated_data.pop('plan', None)
        if plan_data:
            instance.plan = plan_data
        instance.balance = validated_data.get('balance', instance.balance)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.save()
        return instance
