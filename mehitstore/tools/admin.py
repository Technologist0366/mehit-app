from django.contrib import admin
from .models import Tool

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'is_free', 'order', 'created_at']
    list_editable = ['order', 'is_active', 'is_free']
    list_filter = ['is_active', 'is_free']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'icon', 'url')
        }),
        ('Access & Pricing', {
            'fields': ('is_active', 'is_free', 'price', 'stripe_price_id')
        }),
        ('Display Settings', {
            'fields': ('order',)
        }),
    )
