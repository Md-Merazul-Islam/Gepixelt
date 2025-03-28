from django.contrib.auth import login, get_user_model
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
import pandas as pd
from .serializers import WeeklyOrderListSerializer
from .models import WeeklyOrder, OrderItem
from django.http import HttpResponse
from .serializers import WeeklyOrderSerializer, WeeklyOrderListSerializer
from .models import WeeklyOrder
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WeeklyOrder, Product, OrderItem
from django.conf import settings
import stripe

# Initialize Stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class WeeklyOrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract payment info from the request body
            # Payment details: name, email, etc.
            payment_info = request.data.get('payment_info')
            # Total amount for the payment
            total_amount = request.data.get('total_amount')

            if total_amount is None or total_amount <= 0:
                return Response({"error": "Invalid total amount."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 1: Create Payment Intent using Stripe
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert amount to cents
                currency='usd',
            )

            # Return this to the frontend to complete payment
            client_secret = payment_intent.client_secret

            # Respond with the client_secret to complete the payment
            return Response({
                'client_secret': client_secret,
                'message': 'Payment intent created successfully. Please complete the payment.'
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WeeklyOrderConfirmPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract the payment status and order data from the request
            payment_status = request.data.get('payment_status')
            order_data = request.data.get('order_data')
            payment_info = request.data.get('payment_info')
            total_amount = request.data.get('total_amount')

            if payment_status != 'success':
                return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

            stripe_payment_id = request.data.get('stripe_payment_id')
            created_orders = []
            total_week_price = total_amount

            # Process the order data and save it to the database
            for weekly_order_data in order_data:
                weekly_order = WeeklyOrder.objects.create(
                    day_of_week=weekly_order_data['day_of_week'],
                    number_of_people=weekly_order_data['number_of_people'],
                    customer_name=payment_info['name'],
                    customer_email=payment_info['email'],
                    customer_phone=payment_info['phone'],
                    customer_address=payment_info['address'],
                    customer_postal_code=payment_info['postal_code'],
                    stripe_payment_id=stripe_payment_id,
                    total_amount=total_amount
                )

                order_items = []
                for item in weekly_order_data['order_items']:
                    product = Product.objects.get(id=item['product'])

                    order_item = OrderItem.objects.create(
                        weekly_order=weekly_order,
                        product=product,
                        quantity=item['quantity']
                    )
                    order_items.append({
                        'product': product.name,
                        'quantity': order_item.quantity,
                    })

                created_orders.append({
                    'day_of_week': weekly_order.day_of_week,
                    'number_of_people': weekly_order.number_of_people,
                    'order_items': order_items,
                    'total_order_price': total_amount  # Total price of the order
                })

            return Response({
                "message": "Orders created successfully",
                "orders": created_orders,
                "total_week_price": total_amount
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WeeklyOrderListView(ListAPIView):
    queryset = WeeklyOrder.objects.all()  # Get all WeeklyOrder objects
    # Use the WeeklyOrderSerializer for the response
    serializer_class = WeeklyOrderListSerializer

    def get_queryset(self):
        """
        Optionally filter the orders based on query parameters (e.g., day_of_week).
        """
        queryset = WeeklyOrder.objects.all()
        day_of_week = self.request.query_params.get('day_of_week', None)
        if day_of_week:
            queryset = queryset.filter(day_of_week=day_of_week)
        return queryset


# class WeeklyOrderExportToExcelView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Step 1: Fetch all weekly orders or filter by date, if needed
#         orders = WeeklyOrder.objects.prefetch_related('order_items_week')  # Prefetch related order items

#         # Step 2: Serialize the data
#         serialized_data = WeeklyOrderListSerializer(orders, many=True).data

#         # Debugging: Print the serialized data to verify it's being fetched correctly
#         print("Serialized Data:")
#         print(serialized_data)

#         # Step 3: Prepare data for pandas DataFrame
#         data = []

#         # Loop through the serialized data to structure it for the DataFrame
#         for order in serialized_data:
#             print(f"Processing Order ID: {order['id']}")  # Debugging: print current order ID
#             for item in order['order_items']:
#                 print(f"Processing Item: {item['product']['name']} (Quantity: {item['quantity']})")  # Debugging: print item details
#                 data.append({
#                     "Order ID": order['id'],
#                     "Day of Week": order['day_of_week'],
#                     "Number of People": order['number_of_people'],
#                     "Customer Name": order['customer_name'],
#                     "Customer Email": order['customer_email'],
#                     "Customer Phone": order['customer_phone'],
#                     "Customer Address": order['customer_address'],
#                     "Customer Postal Code": order['customer_postal_code'],
#                     "Stripe Payment ID": order['stripe_payment_id'],
#                     "Product Name": item['product']['name'],  # Assuming the product is serialized with 'product.name'
#                     "Quantity": item['quantity'],
#                     "Total Price": item['total_price'],  # Assuming total_price is already computed
#                     "Total Amount": order['total_amount']
#                 })

#         # Debugging: Print the structured data before passing it to DataFrame
#         print("Structured Data for DataFrame:")
#         print(data)

#         # Step 4: Create pandas DataFrame
#         df = pd.DataFrame(data)

#         # Debugging: Print DataFrame before sending as response
#         print("DataFrame:")
#         print(df)

#         # Step 5: Create a response to download the file
#         response = HttpResponse(content_type='application/vnd.ms-excel')
#         response['Content-Disposition'] = 'attachment; filename="weekly_orders.xlsx"'

#         # Step 6: Write the DataFrame to the response as an Excel file
#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False)

#             # Access the workbook and active sheet
#             workbook = writer.book
#             worksheet = workbook.active

#             # Set column widths for better readability
#             worksheet.column_dimensions['A'].width = 15  # Order ID column
#             worksheet.column_dimensions['B'].width = 20  # Customer Name column
#             worksheet.column_dimensions['C'].width = 30  # Customer Email column
#             worksheet.column_dimensions['D'].width = 20  # Customer Phone column
#             worksheet.column_dimensions['E'].width = 40  # Address column
#             worksheet.column_dimensions['F'].width = 15  # Postal Code column
#             worksheet.column_dimensions['G'].width = 15  # Stripe Payment ID column
#             worksheet.column_dimensions['H'].width = 30  # Product Name column
#             worksheet.column_dimensions['I'].width = 15  # Quantity column
#             worksheet.column_dimensions['J'].width = 15  # Total Price column
#             worksheet.column_dimensions['K'].width = 15  # Total Amount column

#             # Set row height for row 1 (header row)
#             worksheet.row_dimensions[1].height = 30

#         return response
class WeeklyOrderExportToExcelView(APIView):
    def get(self, request, *args, **kwargs):
        # Step 1: Fetch all weekly orders, including related order items
        orders = WeeklyOrder.objects.prefetch_related('order_items_week')

        # Step 2: Prepare the data in the desired format
        data = []

        for order in orders:
            order_items = []

            # Loop through each order item and concatenate the product name and quantity
            for item in order.order_items_week.all():
                # Get product name and quantity, then build the string
                product_str = f"{item.product.name} x {item.quantity}"
                order_items.append(product_str)

            # Join all items into one string (e.g., "Product 1 x 2, Product 2 x 1")
            order_items_str = ', '.join(order_items)

            # Multiply the order items string by the number of people
            order_items_with_people = f"({order_items_str}) * {order.number_of_people}"

            # Calculate total amount (you can use this in your response as well)
            total_price_for_order = sum(
                item.product.price * item.quantity for item in order.order_items_week.all()) * order.number_of_people

            # Append the order information to the data list
            data.append({
                "Order ID": order.id,
                "Day of Week": order.day_of_week,
                "Number of People": order.number_of_people,
                "Customer Name": order.customer_name,
                "Customer Email": order.customer_email,
                "Customer Phone": order.customer_phone,
                "Customer Address": order.customer_address,
                "Customer Postal Code": order.customer_postal_code,
                # "Stripe Payment ID": order.stripe_payment_id,
                # This will show the string as per format
                "Order Items": order_items_with_people,
                # "Total Amount": total_price_for_order
            })

        # Step 3: Create pandas DataFrame
        df = pd.DataFrame(data)

        # Step 4: Create a response to download the file as an Excel file
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="weekly_orders.xlsx"'

        # Step 5: Write the DataFrame to the response as an Excel file
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

            # Access the workbook and the active sheet
            workbook = writer.book
            worksheet = workbook.active

            # Set column widths for better readability
            worksheet.column_dimensions['A'].width = 10  # Order ID column
            worksheet.column_dimensions['B'].width = 20  # day name
            # Customer Email column
            worksheet.column_dimensions['C'].width = 5  # person value
            # Customer Phone column
            worksheet.column_dimensions['D'].width = 20  # client name
            worksheet.column_dimensions['E'].width = 40  # email address
            worksheet.column_dimensions['F'].width = 15  # phone number
            # Stripe Payment ID column
            worksheet.column_dimensions['G'].width = 50  # address
            worksheet.column_dimensions['H'].width = 10  # postal code
            worksheet.column_dimensions['I'].width = 60  # Total Amount column

            # Set row height for row 1 (header row)
            worksheet.row_dimensions[1].height = 30

        return response


User = get_user_model()


class OrderStatsView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        # . Total Customers
        total_users = User.objects.count()
        total_customers = WeeklyOrder.objects.values('customer_email').distinct().count()


        # Calculate the start and end of the current week, month, and year
        # Monday of this week
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)  # First day of this month
        start_of_year = today.replace(month=1, day=1)  # First day of this year

        # Total orders, clients, and revenue for this week
        total_orders_week = WeeklyOrder.objects.filter(
            order_date__gte=start_of_week)
        total_clients_week = total_orders_week.values(
            'customer_email').distinct().count()
        total_revenue_week = total_orders_week.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0

        # Total orders, clients, and revenue for this month
        total_orders_month = WeeklyOrder.objects.filter(
            order_date__gte=start_of_month)
        total_clients_month = total_orders_month.values(
            'customer_email').distinct().count()
        total_revenue_month = total_orders_month.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0

        # Total orders, clients, and revenue for this year
        total_orders_year = WeeklyOrder.objects.filter(
            order_date__gte=start_of_year)
        total_clients_year = total_orders_year.values(
            'customer_email').distinct().count()
        total_revenue_year = total_orders_year.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0

        # Calculate revenue for the last 12 months starting from January to the current month
        revenue_last_12_months = []
        for i in range(12):
            # Calculate the month from January onward (first month being January)
            month_idx = i + 1  # 1 is January, 12 is December
            year_idx = today.year if month_idx <= today.month else today.year - 1  # Adjust year if going past January
            start_of_month = today.replace(year=year_idx, month=month_idx, day=1)

            # For the last month (December), calculate the correct end of the month
            if month_idx == 12:
                end_of_month = today.replace(year=year_idx + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = start_of_month.replace(month=start_of_month.month + 1) - timedelta(days=1)

            # Calculate the total revenue for the current month
            revenue_month = WeeklyOrder.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

            revenue_last_12_months.append({
                'month': start_of_month.strftime('%B %Y'),  # e.g. "January 2025"
                'revenue': revenue_month
            })

        # Prepare the response data
        response_data = {
            'total_users': total_users,
            'total_customers': total_customers,
            "total_orders_this_week": total_orders_week.count(),
            "total_clients_this_week": total_clients_week,
            "total_revenue_this_week": total_revenue_week,
            "total_orders_this_month": total_orders_month.count(),
            "total_clients_this_month": total_clients_month,
            "total_revenue_this_month": total_revenue_month,
            "total_orders_this_year": total_orders_year.count(),
            "total_clients_this_year": total_clients_year,
            "total_revenue_this_year": total_revenue_year,
            "revenue_last_12_months": revenue_last_12_months
        }

        return Response(response_data)