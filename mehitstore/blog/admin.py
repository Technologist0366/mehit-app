from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import slugify
from .models import BlogPost, Category, Tag, SourceOrganization, BlogImage  # Add BlogImage

class BlogImageInline(admin.TabularInline):
    """Inline admin for blog gallery images"""
    model = BlogImage
    extra = 3  # Show 3 empty image upload fields
    fields = ['image', 'caption', 'alt_text', 'order', 'is_featured']
    ordering = ['order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(SourceOrganization)
class SourceOrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "website", "rss_feed")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'blog_post', 'thumbnail', 'caption', 'order')
    list_filter = ('blog_post',)
    search_fields = ('blog_post__title', 'caption')
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No image"
    thumbnail.short_description = 'Preview'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    # Add the inline for images
    inlines = [BlogImageInline]

    list_display = (
        "title",
        "category",
        "status",
        "source",
        "published_at",
        "created_at",
        "seo_ready",
        "image_count",  # New field
    )

    list_filter = (
        "status",
        "category",
        "source",
        "created_at",
        "published_at",
    )

    search_fields = (
        "title",
        "content",
        "meta_title",
        "meta_description",
    )

    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at", "image_preview")  # Add image_preview
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        ("Core Content", {
            "fields": (
                "title",
                "slug",
                "excerpt",
                "content",
            )
        }),
        ("Featured Image", {
            "fields": (
                "featured_image",
                "image_preview",  # Preview of featured image
            )
        }),
        ("Classification", {
            "fields": (
                "category",
                "tags",
                "source",
                "source_url",
            )
        }),
        ("SEO Optimization", {
            "fields": (
                "meta_title",
                "meta_description",
            )
        }),
        ("Publishing Workflow", {
            "fields": (
                "author",
                "status",
                "published_at",
            )
        }),
        ("Timestamps", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )

    def seo_ready(self, obj):
        if obj.meta_title and obj.meta_description:
            return format_html('<span style="color:green;">✔ SEO</span>')
        return format_html('<span style="color:red;">✘ SEO</span>')
    seo_ready.short_description = "SEO Status"

    def image_count(self, obj):
        count = obj.gallery_images.count()
        if count > 0:
            return format_html('<span style="color:blue;">{} images</span>', count)
        return "No images"
    image_count.short_description = "Gallery"

    def image_preview(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 200px;" />', obj.featured_image.url)
        return "No featured image"
    image_preview.short_description = "Featured Image Preview"

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        if not obj.slug:
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)