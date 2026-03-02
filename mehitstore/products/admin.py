# apps/products/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for product categories (e.g., Fire Safety, PPE, Electrical Safety)
    """
    list_display = ('name', 'slug', 'product_count', 'view_products_link')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

    def view_products_link(self, obj):
        url = reverse('admin:products_product_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">View Products →</a>', url)
    view_products_link.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for safety & compliance products
    """
    list_display = (
        'thumbnail_preview',
        'name',
        'sku',
        'category',
        'price_display',
        'stock_status',
        'is_active',
        'created_at',
    )
    list_display_links = ('name',)
    list_filter = (
        'category',
        'is_active',
        'created_at',
        'stock',
    )
    search_fields = (
        'name',
        'sku',
        'description',
        'key_features__contains',
        'specifications__contains',
    )
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'image_url_preview', 'datasheet_url_preview')
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'sku',
                'name',
                'slug',
                'category',
                'price',
                'stock',
                'is_active',
            )
        }),
        ('Media & Files', {
            'fields': (
                'image',
                'image_url_preview',
                'datasheet',
                'datasheet_url_preview',
            )
        }),
        ('Content', {
            'fields': (
                'description',
                'key_features',
                'specifications',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('-created_at',)
    list_per_page = 25

    # ─── Custom display methods ────────────────────────────────────────

    def thumbnail_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="60" height="60" '
                f'style="object-fit:cover; border-radius:4px;" />'
            )
        return mark_safe('<span style="color:#999;">No image</span>')
    thumbnail_preview.short_description = "Preview"

    def price_display(self, obj):
        return f"KES {obj.price:,.0f}"
    price_display.short_description = "Price"
    price_display.admin_order_field = 'price'

    def stock_status(self, obj):
        if obj.stock == 0:
            color = "red"
            text = "Out of Stock"
        elif obj.stock <= 5:
            color = "orange"
            text = f"Low ({obj.stock})"
        else:
            color = "green"
            text = f"In Stock ({obj.stock})"
        return mark_safe(f'<span style="color:{color}; font-weight:bold;">{text}</span>')
    stock_status.short_description = "Stock"

    def image_url_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<a href="{}" target="_blank">View Full Image</a><br>'
                '<img src="{}" width="300" style="margin-top:8px; border:1px solid #ddd;" />',
                obj.image_url, obj.image_url
            )
        return "No image uploaded"
    image_url_preview.short_description = "Image Preview"

    def datasheet_url_preview(self, obj):
        if obj.datasheet_url:
            return format_html(
                '<a href="{}" target="_blank">Download Datasheet</a>',
                obj.datasheet_url
            )
        return "No datasheet uploaded"
    datasheet_url_preview.short_description = "Datasheet"

    # ─── Actions ───────────────────────────────────────────────────────

    actions = ['make_active', 'make_inactive', 'clear_stock']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected products as Active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected products as Inactive"

    def clear_stock(self, request, queryset):
        queryset.update(stock=0)
    clear_stock.short_description = "Set stock to 0 (Out of Stock)"