"""
URL configuration for mehit project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Blog
    path('blog/', include('blog.urls')),
    
    # Store (all product-related URLs go under /store/)
    path('store/', include('products.urls')),

    #  policies
    path('policies/', include('policies.urls')),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
