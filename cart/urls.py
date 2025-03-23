from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet, CardItemViewSet

router = DefaultRouter()
router.register(r'carts', CardViewSet, basename='card') # add item and list show
router.register(r'cart-items', CardItemViewSet, basename='cart-item') #update and delete

urlpatterns = [
    path('', include(router.urls)),
]
