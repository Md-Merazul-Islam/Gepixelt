
from django.urls import path
from .views import DashboardStatsView,export_orders_excel

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('export-orders-excel/', export_orders_excel, name='export_orders_excel'),
]
