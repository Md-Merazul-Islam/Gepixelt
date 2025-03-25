from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Allows adding extra order items in the admin panel
    readonly_fields = ('price',)  # Price auto-calculates, so make it read-only

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'receive_date', 'total_price', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username', 'id')
    readonly_fields = ('total_price', 'order_date')
    inlines = [OrderItemInline]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    readonly_fields = ('price',)

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
