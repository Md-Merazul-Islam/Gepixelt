from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Card, CardItem, Product
from .serializers import CardSerializer, CardItemSerializer
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from django.db import transaction
from django.http import Http404
def success_response(message, data, status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }, status=status_code)


def failure_response(message, error, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "statusCode": status_code,
        "message": message,
        "error": error
    }, status=status_code)


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        List all cart items for the authenticated user.
        """
        cart = self.get_queryset()
        if cart.exists():
            serializer = self.get_serializer(cart.first())
            return success_response("Cart retrieved successfully", serializer.data)
        else:
            return success_response("Cart is empty", {})
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add product to the cart.
        No stock checking; products are considered unlimited.
        """
        cart, created = Card.objects.get_or_create(user=request.user)

        try:
            # Attempt to fetch the product based on the given product_id
            product = get_object_or_404(Product, id=request.data.get('product_id'))
        except Http404:
            return failure_response("Product not found", {}, status.HTTP_404_NOT_FOUND)
        quantity = request.data.get('quantity', 1)

        with transaction.atomic():
            cart_item, item_created = CardItem.objects.get_or_create(
                card=cart, product=product
            )
            if item_created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity  # If product already exists, increase quantity

            cart_item.save()

        serializer = CardItemSerializer(cart_item)
        return success_response("Product added to cart", serializer.data, status.HTTP_201_CREATED)
    
    
    
    
class CardItemViewSet(viewsets.ModelViewSet):
    serializer_class = CardItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CardItem.objects.filter(card__user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Update cart item quantity and return updated item details (no stock check).
        """
        cart_item = self.get_object()  # Get the cart item by its ID
        new_quantity = int(request.data.get('quantity', cart_item.quantity))  # New quantity

        # Update the quantity of the cart item
        cart_item.quantity = new_quantity
        cart_item.save()

        # Calculate the total price for the updated cart item
        total_price = cart_item.product.price * cart_item.quantity

        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Cart item updated successfully",
            "data": {
                "id": cart_item.id,
                "product": cart_item.product.id,
                "product_name": cart_item.product.name,
                "quantity": cart_item.quantity,
                "total_price": total_price
            }
        }, status=status.HTTP_200_OK)
        
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific cart item by its ID.
        """
        cart_item = self.get_object()  # Get the cart item by its ID
        total_price = cart_item.product.price * cart_item.quantity

        return Response({
            "success": True,
            "statusCode": status.HTTP_200_OK,
            "message": "Cart item details retrieved successfully",
            "data": {
                "id": cart_item.id,
                "product": cart_item.product.id,
                "product_name": cart_item.product.name,
                "quantity": cart_item.quantity,
                "total_price": total_price
            }
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Remove cart item and update product stock.
        """
        cart_item = self.get_object()
        cart_item.delete()

        return success_response(
          'Cart item removed successfully, stock updated',{},
            status_code=status.HTTP_204_NO_CONTENT
        )