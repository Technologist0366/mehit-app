from django.contrib import admin
from .models import PolicyTemplate, Policy

@admin.register(PolicyTemplate)
class PolicyTemplateAdmin(admin.ModelAdmin):
    list_display = ['name',  'version', 'is_active', 'created_at']
    list_filter = [ 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name' , 'description', 'version', 'is_active')
        }),
        ('Template Content', {
            'fields': ('content_structure',),
            'classes': ('wide',),
            'description': 'JSON must contain an "html" key with the template.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'status', 'effective_date', 'created_at']
    list_filter = ['status', 'effective_date']
    search_fields = ['user__email', 'title', 'slug']
    readonly_fields = ['created_at', 'updated_at', 'slug', 'generated_content', 'pdf_file', 'qr_code']
    fieldsets = (
        (None, {
            'fields': ('user', 'template', 'title', 'slug', 'status', 'effective_date')
        }),
        ('Generated Content', {
            'fields': ('generated_content', 'pdf_file', 'qr_code'),
            'classes': ('wide',),
        }),
        ('Responses (raw)', {
            'fields': ('responses',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )
