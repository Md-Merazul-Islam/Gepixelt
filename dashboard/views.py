from django.db import models
from django.contrib.auth import login, get_user_model
from orders.models import Order, OrderItem
from payments.models import SubscriptionPlan,UserSubscription,Transaction
User = get_user_model()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from decimal import Decimal

class DashboardStatsView(APIView):

    def get(self, request):
        # 1. Total Customers
        total_customers = User.objects.count()

        # 2. Total Orders Today
        today = timezone.now().date()
        total_orders_today = Order.objects.filter(order_date__date=today).count()

        # 3. Total Subscriptions
        total_subscriptions = UserSubscription.objects.filter(status='active').count()

        # 4. Yearly Revenue
        start_of_year = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        total_revenue_yearly = Order.objects.filter(order_date__gte=start_of_year).aggregate(
            total_revenue=Sum('total_price')
        )['total_revenue'] or Decimal('0.00')  # Default to 0.00 if no revenue exists

        data = {
            "total_customers": total_customers,
            "total_orders_today": total_orders_today,
            "total_subscriptions": total_subscriptions,
            "total_revenue_yearly": str(total_revenue_yearly)  # Convert Decimal to string for JSON serialization
        }

        return Response(data, status=status.HTTP_200_OK)