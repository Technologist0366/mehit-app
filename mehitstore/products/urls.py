from django.urls import path
from . import views

urlpatterns = [
    # STORE FRONT - Main store page
    # URL: /store/
    path('', views.store_front, name='store-front'),
    
    # API ENDPOINTS - For JavaScript fetch requests
    # URL: /store/api/products/
    path('api/products/', views.api_products, name='api-products'),
    
    # URL: /store/api/products/<id>/
    path('api/products/<int:product_id>/', views.api_product_detail, name='api-product-detail'),
    
    # URL: /store/api/categories/
    path('api/categories/', views.api_categories, name='api-categories'),
    
    # URL: /store/api/sectors/
    path('api/sectors/', views.api_sectors, name='api-sectors'),
    
    # URL: /store/api/certifications/
    path('api/certifications/', views.api_certifications, name='api-certifications'),
    
    # PRODUCT DETAIL PAGES - Individual product by slug
    # URL: /store/<slug:slug>/
    path('<slug:slug>/', views.ProductDetail.as_view(), name='product-detail'),
]
