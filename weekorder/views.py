import logging
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now

from django.db.models import Sum
import pandas as pd
from .serializers import WeeklyOrderListSerializer
from .models import WeeklyOrder, OrderItem
from django.http import HttpResponse
from .serializers import WeeklyOrderListSerializer
from .models import WeeklyOrder
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WeeklyOrder, Product, OrderItem
from django.conf import settings
import stripe
import paypalrestsdk
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class WeeklyOrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            total_amount = request.data.get('total_amount')
            if total_amount is None or total_amount <= 0:
                return Response({"error": "Invalid total amount."}, status=status.HTTP_400_BAD_REQUEST)
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),
                currency='usd',
            )
            client_secret = payment_intent.client_secret
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'client_secret': client_secret,

                'message': 'Payment intent created successfully. Please complete the payment.'
            }, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Setup logger
logger = logging.getLogger(__name__)


class WeeklyOrderConfirmPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payment_status = request.data.get('payment_status')
            order_data = request.data.get('order_data')
            payment_info = request.data.get('payment_info')
            total_amount = request.data.get('total_amount')

            # Log the input data
            logger.info("Received payment status: %s", payment_status)
            logger.info("Received order data: %s", order_data)
            logger.info("Received payment info: %s", payment_info)
            logger.info("Received total amount: %s", total_amount)
            # logger.info("Received Stripe payment ID: %s", stripe_payment_id)

            if payment_status != 'success':
                return Response({"error": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

            stripe_payment_id = request.data.get('stripe_payment_id')
            created_orders = []
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
                    'total_order_price': total_amount
                })

            return Response({
                "message": "Orders created successfully",
                "orders": created_orders,
                "total_week_price": total_amount
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class WeeklyOrderListView(ListAPIView):
    queryset = WeeklyOrder.objects.all()
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
#         orders = WeeklyOrder.objects.prefetch_related('order_items_week')
#         data = []

#         for order in orders:
#             order_items = []
#             for item in order.order_items_week.all():
#                 product_str = f"{item.product.name} x {item.quantity}"
#                 order_items.append(product_str)
#             order_items_str = ', '.join(order_items)
#             order_items_with_people = f"({order_items_str}) * {order.number_of_people}"

#             data.append({
#                 "Order ID": order.id,
#                 "Day of Week": order.day_of_week,
#                 "Number of People": order.number_of_people,
#                 "Customer Name": order.customer_name,
#                 "Customer Email": order.customer_email,
#                 "Customer Phone": order.customer_phone,
#                 "Customer Address": order.customer_address,
#                 "Customer Postal Code": order.customer_postal_code,
#                 "Order Items": order_items_with_people,
#             })

#         df = pd.DataFrame(data)
#         response = HttpResponse(content_type='application/vnd.ms-excel')
#         response['Content-Disposition'] = 'attachment; filename="weekly_orders.xlsx"'

#         with pd.ExcelWriter(response, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False)
#             workbook = writer.book
#             worksheet = workbook.active
#             worksheet.column_dimensions['A'].width = 10
#             worksheet.column_dimensions['B'].width = 20
#             worksheet.column_dimensions['C'].width = 5
#             worksheet.column_dimensions['D'].width = 20
#             worksheet.column_dimensions['E'].width = 40
#             worksheet.column_dimensions['F'].width = 15
#             worksheet.column_dimensions['G'].width = 50
#             worksheet.column_dimensions['H'].width = 10
#             worksheet.column_dimensions['I'].width = 60
#             worksheet.row_dimensions[1].height = 30
#         return response


User = get_user_model()


class OrderStatsView(APIView):
    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        total_users = User.objects.count()
        total_customers = WeeklyOrder.objects.values(
            'customer_email').distinct().count()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        total_orders_week = WeeklyOrder.objects.filter(
            order_date__gte=start_of_week)
        total_clients_week = total_orders_week.values(
            'customer_email').distinct().count()
        total_revenue_week = total_orders_week.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0
        total_orders_month = WeeklyOrder.objects.filter(
            order_date__gte=start_of_month)
        total_clients_month = total_orders_month.values(
            'customer_email').distinct().count()
        total_revenue_month = total_orders_month.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0

        total_orders_year = WeeklyOrder.objects.filter(
            order_date__gte=start_of_year)
        total_clients_year = total_orders_year.values(
            'customer_email').distinct().count()
        total_revenue_year = total_orders_year.aggregate(
            Sum('total_amount'))['total_amount__sum'] or 0

        revenue_last_12_months = []
        for i in range(12):
            month_idx = i + 1
            year_idx = today.year if month_idx <= today.month else today.year - 1
            start_of_month = today.replace(
                year=year_idx, month=month_idx, day=1)

            if month_idx == 12:
                end_of_month = today.replace(
                    year=year_idx + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_of_month = start_of_month.replace(
                    month=start_of_month.month + 1) - timedelta(days=1)

            revenue_month = WeeklyOrder.objects.filter(order_date__gte=start_of_month, order_date__lte=end_of_month).aggregate(
                Sum('total_amount'))['total_amount__sum'] or 0

            revenue_last_12_months.append({

                'month': start_of_month.strftime('%B %Y'),
                'revenue': revenue_month
            })

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


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


class WeeklyOrderCreateByPayPal(APIView):
    def post(self, request, *args, **kwargs):
        try:
            total_amount = request.data.get('total_amount')
            if total_amount is None or total_amount <= 0:
                return JsonResponse({"error": "Invalid total amount."}, status=status.HTTP_400_BAD_REQUEST)
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(total_amount),
                        "currency": "USD"
                    },
                    "description": "Weekly Order Payment"
                }],
                "redirect_urls": {
                    "return_url": "http://localhost:3000/payment/paymentSuccess",
                    "cancel_url": "http://localhost:3000/payment/paymentFail"
                }
            })

            if payment.create():
                paypal_redirect_url = next(
                    link.href for link in payment.links if link.rel == "approval_url")

                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment created successfully.',
                    'payment_id': payment.id,
                    'paypal_redirect_url': paypal_redirect_url,
                    'message': 'Payment created. Please complete the payment via PayPal.'
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"error": "PayPal payment creation failed."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
# views.py

class WeeklyOrderConfirmByPayPalPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Log the incoming request data for debugging
            print("Incoming request data:", request.data)

            payment_id = request.data.get('paymentId')
            payer_id = request.data.get('PayerID')

            if not payment_id or not payer_id:
                return JsonResponse({"error": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST)

            # Find the payment using the PayPal API
            payment = paypalrestsdk.Payment.find(payment_id)

            # Log payment details for debugging
            print("PayPal payment details:", payment)

            # Ensure the payment state is 'COMPLETED'
            if payment.state == "COMPLETED":
                # Execute the payment using the payer_id to confirm the payment
                if payment.execute({"payer_id": payer_id}):
                    # If payment is successful, process the order and create it in the database
                    order_data = request.data.get('order_data')
                    payment_info = request.data.get('payment_info')
                    total_amount = request.data.get('total_amount')

                    created_orders = []
                    for weekly_order_data in order_data:
                        # Create the weekly order
                        weekly_order = WeeklyOrder.objects.create(
                            day_of_week=weekly_order_data['day_of_week'],
                            number_of_people=weekly_order_data['number_of_people'],
                            customer_name=payment_info['name'],
                            customer_email=payment_info['email'],
                            customer_phone=payment_info['phone'],
                            customer_address=payment_info['address'],
                            customer_postal_code=payment_info['postal_code'],
                            total_amount=total_amount
                        )

                        # Create the order items
                        for item in weekly_order_data['order_items']:
                            product = Product.objects.get(id=item['product'])
                            OrderItem.objects.create(
                                weekly_order=weekly_order,
                                product=product,
                                quantity=item['quantity']
                            )

                        created_orders.append({
                            'day_of_week': weekly_order.day_of_week,
                            'number_of_people': weekly_order.number_of_people,
                            'total_order_price': total_amount
                        })

                    return JsonResponse({
                        "message": "Orders created successfully",
                        "orders": created_orders,
                        "total_week_price": total_amount
                    }, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({"error": "Payment execution failed."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Log the actual payment state for debugging
                print(f"Payment state: {payment.state}")
                return JsonResponse({"error": f"Payment not approved by PayPal. Current state: {payment.state}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class WeeklyOrderExportToExcelView(APIView):
    def get(self, request, *args, **kwargs):
        today = now().date() 
        day_name = request.GET.get('day_name', None) 

        if day_name:
                orders = WeeklyOrder.objects.filter(day_of_week=day_name).prefetch_related('order_items_week')
        else:
            
            orders = WeeklyOrder.objects.prefetch_related('order_items_week')

        
        if not orders:
            print(f"No orders found for {day_name}.")

        
        if not orders:
            orders = [{
                "Order ID": "",
                "Receive Day": "",
                "Number of People": "",
                "Customer Name": "",
                "Customer Email": "",
                "Customer Phone": "",
                "Customer Address": "",
                "Customer Postal Code": "",
                "Order Items": "",
                "Created At": "",
            }]
        
        data = []
        
        for order in orders:
            if isinstance(order, dict):  
                data.append(order)
            else:  
                order_items = []
                for item in order.order_items_week.all():
                    product_str = f"{item.product.name} x {item.quantity}"
                    order_items.append(product_str)
                order_items_str = ', '.join(order_items)
                order_items_with_people = f"({order_items_str}) * {order.number_of_people}"

                data.append({
                    "Order ID": order.id,
                    "Receive Day": order.day_of_week,
                    "Number of People": order.number_of_people,
                    "Customer Name": order.customer_name,
                    "Customer Email": order.customer_email,
                    "Customer Phone": order.customer_phone,
                    "Customer Address": order.customer_address,
                    "Customer Postal Code": order.customer_postal_code,
                    "Order Items": order_items_with_people,
                    "Created At": order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                })

        
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="weekly_orders.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            workbook = writer.book
            worksheet = workbook.active

            worksheet.column_dimensions['A'].width = 10
            worksheet.column_dimensions['B'].width = 20
            worksheet.column_dimensions['C'].width = 5
            worksheet.column_dimensions['D'].width = 20
            worksheet.column_dimensions['E'].width = 40
            worksheet.column_dimensions['F'].width = 15
            worksheet.column_dimensions['G'].width = 50
            worksheet.column_dimensions['H'].width = 10
            worksheet.column_dimensions['I'].width = 60
            worksheet.column_dimensions['I'].width = 60

            worksheet.row_dimensions[1].height = 30

        return response