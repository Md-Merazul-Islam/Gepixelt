from decimal import Decimal
from utils.IsAdminOrStaff import IsAdminOrStaff
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import models
from django.contrib.auth import login, get_user_model
from orders.models import Order, OrderItem
from payments.models import SubscriptionPlan, UserSubscription, Transaction
User = get_user_model()


def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    if 'non_field_errors' in error:
        error_message = error['non_field_errors'][0]
    else:
        error_message = error

    return Response({
        "success": False,
        "statusCode": status_code,
        "message": message,
        "error": {
            "message": error_message
        }
    }, status=status_code)


class DashboardStatsView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        # 1. Total Customers
        total_customers = User.objects.count()

        # 2. Total Orders Today
        today = timezone.now().date()
        total_orders_today = Order.objects.filter(
            order_date__date=today).count()

        # 3. Total Subscriptions
        total_subscriptions = UserSubscription.objects.filter(
            status='active').count()

        # 4. Yearly Revenue
        start_of_year = timezone.now().replace(month=1, day=1, hour=0,
                                               minute=0, second=0, microsecond=0)
        total_revenue_yearly = Order.objects.filter(order_date__gte=start_of_year).aggregate(
            total_revenue=Sum('total_price')
            # Default to 0.00 if no revenue exists
        )['total_revenue'] or Decimal('0.00')

        # 5. Monthly Revenue
        monthly_revenue = {}
        for month in range(1, 13):  # Loop through months 1 to 12
            start_of_month = timezone.now().replace(month=month, day=1, hour=0,
                                                    minute=0, second=0, microsecond=0)
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - \
                timedelta(seconds=1)  # Get the last day of the month

            # Aggregate revenue for the month
            monthly_revenue[month] = Order.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(
                total_revenue=Sum('total_price')
                # Default to 0.00 if no revenue exists for the month
            )['total_revenue'] or Decimal('0.00')

        # Prepare the data to return in the response
        data = {
            "total_customers": total_customers,
            "total_orders_today": total_orders_today,
            "total_subscriptions": total_subscriptions,
            # Convert Decimal to string for JSON serialization
            "total_revenue_yearly": str(total_revenue_yearly),
            # Convert all monthly amounts to string
            "monthly_revenue": {month: str(amount) for month, amount in monthly_revenue.items()}
        }

        # return Response(data, status=status.HTTP_200_OK)
        return success_response("Dashboard stats retrieved successfully.", data, status.HTTP_200_OK)
