# serializers.py
from rest_framework import serializers
from .models import Product, Category
from utils.upload_utils import upload_file_to_digital_ocean

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    # Include the category info in the product serializer
    # category = CategorySerializer()
    
    # Temporary field to accept the image during product creation or update
    image_tmp = serializers.FileField(write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'image_tmp']
        read_only_fields = ['image']
    
    def create(self, validated_data):
        """
        Handle product creation, uploading the image to DigitalOcean and saving the product.
        """
        image_tmp = validated_data.pop('image_tmp', None)

        # Validate if image_tmp exists
        if not image_tmp:
            raise serializers.ValidationError({"image_tmp": "An image file must be provided."})
        
        # Upload the image to DigitalOcean and get the URL
        uploaded_image = upload_file_to_digital_ocean(image_tmp)
        validated_data['image'] = uploaded_image
        
        # Create the product
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Handle product updates. Image upload is optional, only update image if provided.
        """
        image_tmp = validated_data.pop('image_tmp', None)

        # If image_tmp exists, upload it to DigitalOcean
        if image_tmp:
            uploaded_image = upload_file_to_digital_ocean(image_tmp)
            validated_data['image'] = uploaded_image

        # Update the rest of the fields dynamically
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
