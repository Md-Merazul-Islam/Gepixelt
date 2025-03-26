from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from utils.IsAdminOrStaff import IsAdminOrStaff
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction
import logging
from datetime import date
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, OrderStatusUpdateSerializer
from utils  .utils import success_response, failure_response
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from django.core.mail import send_mail
from django.template.loader import render_to_string


def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({"success": True, "statusCode": status_code, "message": message, "data": data}, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "statusCode": status_code, "message": message, "error": error}, status=status_code)


class OrderFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=Order.STATUS_CHOICES, label='Order Status')
    order_date = filters.DateFromToRangeFilter(label='Order Date')
    receive_date = filters.DateFromToRangeFilter(label='Receive Date')

    class Meta:
        model = Order
        fields = ['status', 'order_date']


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrStaff]
    pagination_class = OrderPagination
    filter_class = OrderFilter

    def perform_create(self, serializer):
        """Override to set the user for the order."""
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """Override list to apply pagination, filtering, sorting with custom response."""
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)

        # Sorting
        sort_by = request.query_params.get('sort_by', 'order_date')
        if sort_by not in ['order_date', 'status', 'receive_date']:
            sort_by = 'order_date'
        sorted_queryset = filtered_queryset.order_by(sort_by)

        # Pagination
        page = self.paginate_queryset(sorted_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
            return success_response("All orders retrieved successfully", paginated_data)

        # Without pagination
        serializer = self.get_serializer(sorted_queryset, many=True)
        return success_response("All orders retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        """Override create to use success_response."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response("Order created successfully", serializer.data, status.HTTP_201_CREATED)
        return failure_response("Order creation failed", serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to use success_response."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Order details retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        """Override update to use success_response."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data)
        return failure_response("Order update failed", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        """Override destroy to use success_response."""
        instance = self.get_object()
        instance.delete()
        return success_response("Order deleted successfully", {}, status.HTTP_204_NO_CONTENT)


class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        """Retrieve a list of orders or a single order for the authenticated user."""
        if order_id:
            # Retrieve a specific order by ID
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                serializer = OrderSerializer(order)
                return success_response("Order retrieved successfully", serializer.data, status.HTTP_200_OK)
            except Order.DoesNotExist:
                return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to view it.", status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all orders for the authenticated user
            orders = Order.objects.filter(user=request.user).annotate(
                status_order=Case(
                    When(status='pending', then=Value(1)),
                    When(status='accepted', then=Value(2)),
                    When(status='canceled', then=Value(3)),
                    When(status='delivered', then=Value(4)),
                    default=Value(5),  # In case there are unknown statuses
                    output_field=IntegerField()
                )
            ).order_by('status_order')
            serializer = OrderSerializer(orders, many=True)
            return success_response("My Orders retrieved successfully", serializer.data, status.HTTP_200_OK)

    def post(self, request):
        """Create a new order for the authenticated user."""
        # Pass the request into the serializer context
        serializer = OrderSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            # Associate the order with the authenticated user
            order = serializer.save(user=request.user)

            # Dynamically calculate the total amount of the order
            # Assuming `items` is a related field
            total_amount = sum(
                item.price * item.quantity for item in order.items.all())

            # Send order confirmation email to the user
            user_subject = f"Order Confirmation - Order ID: {order.id}"
            user_message = render_to_string(
                'order_confirmation.html', {
                    'user': request.user,
                    'order': order,
                    'order_items': order.items.all(),
                    'total_amount': total_amount  # Pass the calculated total amount
                })

            # Use EmailMessage to send the HTML email
            user_email = EmailMessage(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email]
            )
            user_email.content_subtype = "html"  # Set the content type to HTML
            user_email.send(fail_silently=False)

            # Optionally, send a notification email to the admin
            admin_subject = f"New Order Received - Order ID: {order.id}"
            admin_message = render_to_string(
                'admin_order_notification.html', {
                    'user': request.user,
                    'order': order,
                    'order_items': order.items.all(),
                    'total_amount': total_amount
                })

            # Assuming the admin's email is set in your settings
            admin_email = settings.ADMIN_EMAIL

            admin_email_message = EmailMessage(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email]
            )
            admin_email_message.content_subtype = "html"  # Set the content type to HTML
            admin_email_message.send(fail_silently=False)
            return success_response("Order created successfully", serializer.data, status.HTTP_201_CREATED)

    def put(self, request, order_id):
        """Update an existing order for the authenticated user."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to update it.", status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(
            order, data=request.data, partial=False)  # Full update
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data, status.HTTP_200_OK)
        return failure_response("Order update failed", serializer.errors, status.HTTP_400_BAD_REQUEST)

    def patch(self, request, order_id):
        """Partially update an existing order for the authenticated user."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return failure_response("Order not found", "Order with this ID doesn't exist or you don't have permission to update it.", status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(
            order, data=request.data, partial=True)  # Partial update
        if serializer.is_valid():
            serializer.save()
            return success_response("Order updated successfully", serializer.data, status.HTTP_200_OK)
        return failure_response("Order update failed", serializer.errors, status.HTTP_400_BAD_REQUEST)


class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        """Cancel an existing order for the authenticated user and process refund."""
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # If the order is already canceled, prevent further action
            if order.status == 'canceled':
                return Response(
                    {"success": False,
                        "message": "Order with this ID has already been canceled."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mark the order as canceled
            order.status = 'canceled'
            order.save()

            # Refund the order
            success, result = order.refund_order()

            if success:
                # Return the updated order and user balance after refund
                return Response(
                    {
                        "success": True,
                        "message": "Order canceled successfully",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "total_price": str(order.total_price),
                            "user_balance": str(result),
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"success": False, "message": f"Refund failed: {result}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Order.DoesNotExist:
            return Response(
                {"success": False, "message": "Order not found or you don't have permission to cancel it."},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderStatusUpdateView(APIView):
    """
    View to update the status of an order.
    Accepts PATCH requests with `status` in the request body.
    """

    def patch(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use the serializer to validate and update the status
        serializer = OrderStatusUpdateSerializer(
            order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Order status updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
