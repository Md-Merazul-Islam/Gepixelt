from datetime import datetime, date
from orders.models import Order
from rest_framework.decorators import api_view
from django.http import HttpResponse
import pandas as pd
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


def convert_to_naive_datetime(dt):
    """Helper function to convert timezone-aware datetime to naive datetime."""
    if isinstance(dt, datetime):  # Check if it's a datetime object (with time)
        if timezone.is_aware(dt):
            # Convert to naive
            return timezone.localtime(dt).replace(tzinfo=None)
        return dt  # Already naive, return as is
    return dt  # If it's a date object, return as is


@api_view(['GET'])
def export_orders_excel(request):
    # Get today's date as default if no date is provided
    today = datetime.today().date()

    # Get the date filter from the request (default is today's date)
    # Default to today's date if no date is provided
    date_filter = request.GET.get('receive_date', str(today))
    filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()

    # Fetch orders with related order items and user, and filter by receive_date
    orders = Order.objects.prefetch_related('items').select_related(
        'user').filter(receive_date=filter_date)

    data = []

    for order in orders:
        customer_name = order.user.username
        customer_email = order.user.email
        customer_number = order.user.phone_number
        address = order.user.address
        city = order.user.city
        postal_code = order.user.postal_code
        order_items = []

        # Convert datetime fields to timezone-unaware (if they are timezone-aware)
        order_date = convert_to_naive_datetime(order.order_date)
        receive_date = convert_to_naive_datetime(order.receive_date)

        # Calculate total price for the order by summing the prices of all order items
        # Sum of all item prices
        total_order_price = sum(item.price for item in order.items.all())

        # Iterate through related order items
        for item in order.items.all():  # Use 'items' instead of 'order_items'
            order_items.append({
                "product": item.product.name,  # Assuming `product.name` exists
                "quantity": item.quantity,
                # Convert price to string if it's a decimal field
                "price": str(item.price)
            })

        # Append the order data
        data.append({
            "order_id": order.id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_number": customer_number,
            "address": address,
            "city": city,
            "postal_code": postal_code,
            "order_date": order_date,  # Now correctly handled datetime or date
            "receive_date": receive_date,  # Now correctly handled date
            # Calculate and convert total price to string
            "total_price": str(total_order_price),
            "status": order.status,
            "items": order_items
        })

    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data)

    # Create a response to download the file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="all_orders.xlsx"'

    # Use pandas to write the data to Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

        # Access the workbook and the active sheet
        workbook = writer.book
        worksheet = workbook.active

        # Set column widths (example for a few columns)
        worksheet.column_dimensions['A'].width = 15  # Order ID column
        worksheet.column_dimensions['B'].width = 20  # Customer Name column
        worksheet.column_dimensions['C'].width = 30  # Customer Email column
        worksheet.column_dimensions['D'].width = 20  # Customer Number column
        worksheet.column_dimensions['E'].width = 40  # Address column
        worksheet.column_dimensions['F'].width = 15  # City column
        worksheet.column_dimensions['G'].width = 15  # Postal Code column
        worksheet.column_dimensions['H'].width = 30 #ordered_date
        worksheet.column_dimensions['I'].width = 30 #receive_date
        worksheet.column_dimensions['J'].width = 15 #total_price
        worksheet.column_dimensions['K'].width = 15 #status
        worksheet.column_dimensions['L'].width = 15 #items
        worksheet.column_dimensions['L'].h = 15 #items

         # Set row height for row 1 (header row)
        worksheet.row_dimensions[1].height = 30  # Set height of row 1 (header) to 30

    return response
