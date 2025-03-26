# views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .permissions import IsAdminOrHasRoleAdmin  # Import the custom permission
from rest_framework.pagination import PageNumberPagination
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



class CustomPagination(PageNumberPagination):
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow client to set `page_size` parameter
    max_page_size = 100  # Maximum page size allowed
# Read-only Category ViewSet
class ReadOnlyCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class=CustomPagination
    permission_classes = [AllowAny]  # Allow public access to the API

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return Response({
            "success": True,
            "message": "Category list retrieved successfully",
            "data": serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response({
            "success": True,
            "message": "Category details retrieved successfully",
            "data": serializer.data
        })


# Read-only Product ViewSet
class ReadOnlyProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  
    pagination_class=CustomPagination
    def get_queryset(self):
        category_id = self.request.query_params.get('category', None)
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()

    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        page = self.paginate_queryset(products)  # Apply pagination to the queryset
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return success_response("Product list retrieved successfully", serializer.data)


    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return Response({
            "success": True,
            "message": "Product details retrieved successfully",
            "data": serializer.data
        })

# Category ViewSet with custom responses
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # Default permission for list and retrieve (GET)
    permission_classes = [IsAdminOrHasRoleAdmin]  # Public access to the API

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()
        serializer = self.get_serializer(categories, many=True)
        return success_response("Category list retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return success_response("Category created successfully", CategorySerializer(category).data, status.HTTP_201_CREATED)
        return failure_response("Category creation failed", serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category)
        return success_response("Category details retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=False)
        if serializer.is_valid():
            category = serializer.save()
            return success_response("Category updated successfully", CategorySerializer(category).data)
        return failure_response("Category update failed", serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            return success_response("Category partially updated successfully", CategorySerializer(category).data)
        return failure_response("Category partial update failed", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return success_response("Category deleted successfully", {}, status.HTTP_204_NO_CONTENT)


    
# Product ViewSet with custom responses
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminOrHasRoleAdmin]


    def get_queryset(self):
        category_id = self.request.query_params.get('category', None)
        if category_id:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.all()

    # Override get_permissions to handle different permissions for different methods
    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        page = self.paginate_queryset(products)  # Apply pagination to the queryset
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(products, many=True)
        return success_response("Product list retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return success_response("Product created successfully", ProductSerializer(product).data, status.HTTP_201_CREATED)
        return failure_response("Product creation failed", serializer.errors)

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product)
        return success_response("Product details retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=False)
        if serializer.is_valid():
            product = serializer.save()
            return success_response("Product updated successfully", ProductSerializer(product).data)
        return failure_response("Product update failed", serializer.errors)

    def partial_update(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            return success_response("Product partially updated successfully", ProductSerializer(product).data)
        return failure_response("Product partial update failed", serializer.errors)

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return success_response("Product deleted successfully", {}, status.HTTP_204_NO_CONTENT)
