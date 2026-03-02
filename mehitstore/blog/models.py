from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    # ... (keep your existing Category model)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    # ... (keep your existing Tag model)
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SourceOrganization(models.Model):
    # ... (keep your existing SourceOrganization model)
    name = models.CharField(max_length=255)
    website = models.URLField()
    rss_feed = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    # ... (keep your existing BlogPost fields)
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("review", "In Review"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    source = models.ForeignKey(SourceOrganization, on_delete=models.SET_NULL, null=True, blank=True)
    source_url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    featured_image = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ===== NEW MODEL FOR MULTIPLE IMAGES =====
class BlogImage(models.Model):
    """Gallery images for blog posts"""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='blog_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, help_text="SEO: Describe the image")
    order = models.PositiveIntegerField(default=0, help_text="Order to display images")
    is_featured = models.BooleanField(default=False, help_text="Use as additional featured image")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.blog_post.title}"