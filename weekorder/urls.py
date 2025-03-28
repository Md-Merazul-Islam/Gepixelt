# urls.py

from django.urls import path, include

from .views import WeeklyOrderCreateView
urlpatterns = [
     path('order/',WeeklyOrderCreateView.as_view(), name='order-status-update'),
]
