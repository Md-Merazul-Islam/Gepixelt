from django.contrib import admin
from .models import WeeklyOrder, OrderItem
from products.models import Product

# OrderItem Inline for WeeklyOrder
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # This adds an extra empty form to add new order items

# WeeklyOrderAdmin to manage WeeklyOrder and related OrderItems
class WeeklyOrderAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'customer_name', 'customer_email', 'number_of_people', 'total_price', 'stripe_payment_id')
    search_fields = ('day_of_week', 'customer_name', 'customer_email')
    list_filter = ('day_of_week', 'number_of_people')

    # Include the inline OrderItems in the WeeklyOrder admin page
    inlines = [OrderItemInline]

    # Make total_price a read-only field (since it's calculated)
    readonly_fields = ('total_price',)

# Register the WeeklyOrder model in the admin
admin.site.register(WeeklyOrder, WeeklyOrderAdmin)

# Register the OrderItem model in the admin
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('weekly_order', 'product', 'quantity', 'total_price')
    search_fields = ('weekly_order__day_of_week', 'product__name')

admin.site.register(OrderItem, OrderItemAdmin)
