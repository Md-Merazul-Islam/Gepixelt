# Generated by Django 5.1.7 on 2025-03-24 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_remove_order_product_orderproduct_order_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='quantity',
        ),
        migrations.AddField(
            model_name='order',
            name='create_date',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
