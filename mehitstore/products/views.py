from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductSerializer

# ========== CLASS-BASED VIEWS ==========
class ProductList(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category__slug', 'price']

class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'

# ========== STORE FRONT VIEW ==========
def store_front(request):
    """Render the main store page"""
    return render(request, 'store.html')
def api_products(request):
    """Return all products as JSON for the store frontend"""
    products = Product.objects.filter(is_active=True).select_related('category')
    data = []
    for product in products:
        data.append({
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'category': product.category.name if product.category else '',
            'category_slug': product.category.slug if product.category else '',
            'image_url': product.image_url,
            'description': product.description[:200] + '...' if product.description else '',
            'key_features': product.key_features[:4] if product.key_features else [],
            'in_stock': product.in_stock,
            'low_stock': product.low_stock,
        })
    return JsonResponse(data, safe=False)


def api_product_detail(request, product_id):
    """Return a single product's details as JSON"""
    try:
        product = Product.objects.select_related('category').get(id=product_id, is_active=True)
        data = {
            'id': product.id,
            'sku': product.sku,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'category': product.category.name if product.category else '',
            'category_slug': product.category.slug if product.category else '',
            'image_url': product.image_url,
            'datasheet_url': product.datasheet_url,
            'description': product.description,
            'key_features': product.key_features,
            'specifications': product.specifications,
            'stock': product.stock,
            'in_stock': product.in_stock,
            'created_at': product.created_at,
            'updated_at': product.updated_at,
        }
        return JsonResponse(data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def api_sectors(request):
    """Return unique sectors from products"""
    sectors = set()
    for product in Product.objects.filter(is_active=True):
        if hasattr(product, 'sectors') and product.sectors:
            if isinstance(product.sectors, list):
                for sector in product.sectors:
                    sectors.add(sector)
    data = [{'id': s, 'name': s.replace('-', ' ').title()} for s in sectors]
    return JsonResponse(data, safe=False)


def api_certifications(request):
    """Return unique certifications from products"""
    certs = set()
    for product in Product.objects.filter(is_active=True):
        if hasattr(product, 'certifications') and product.certifications:
            if isinstance(product.certifications, list):
                for cert in product.certifications:
                    certs.add(cert)
    data = [{'id': c, 'name': c.upper()} for c in certs]
    return JsonResponse(data, safe=False)

def api_categories(request):
    """Return all categories as JSON"""
    categories = Category.objects.filter(is_active=True)
    data = [{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'product_count': cat.products.filter(is_active=True).count()
    } for cat in categories]
    return JsonResponse(data, safe=False)

