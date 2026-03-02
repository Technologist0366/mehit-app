from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    image_url = serializers.ReadOnlyField()
    datasheet_url = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'slug', 'category', 'category_id',
            'price', 'description', 'key_features', 'specifications',
            'image_url', 'datasheet_url', 'stock', 'is_active',
            'created_at', 'updated_at'
        ]