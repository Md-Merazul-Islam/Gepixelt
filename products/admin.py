from django.contrib import admin
from .models import Category, Product

class CategoryAdmin(admin.ModelAdmin):
    # Display the 'name' and 'slug' fields in the list view
    list_display = ('name', 'slug')
    
    # Add a search bar for easy searching by category name
    search_fields = ['name']
    
    # Allow slug field to be automatically populated
    prepopulated_fields = {'slug': ('name',)}

    # Make 'name' and 'slug' fields editable directly from the list view
    list_editable = ('slug',)

class ProductAdmin(admin.ModelAdmin):
    # Display the fields in the list view
    list_display = ('name','main_price', 'price', 'category')
    
    # Allow searching by product name and description
    search_fields = ['name', 'description']
    
    # Filter products by category
    list_filter = ('category',)

    # Ensure that 'category' can be selected from a dropdown
    list_editable = ('category',)

# Register models with the admin site
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
