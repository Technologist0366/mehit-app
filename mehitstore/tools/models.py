import uuid
from django.db import models
from django.urls import reverse

class Tool(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Used in URLs, e.g., 'privacy-generator'")
    description = models.TextField()

    # Icon (Font Awesome class, e.g., "fas fa-file-contract")
    icon = models.CharField(max_length=100, default="fas fa-cog", help_text="Font Awesome icon class")

    # URL – can be absolute or relative path
    url = models.CharField(max_length=500, help_text="Relative path like '/policies/questionnaire/' or full URL")

    # Status and access
    is_active = models.BooleanField(default=True, help_text="Show on tools page")
    is_free = models.BooleanField(default=True, help_text="If False, requires payment/subscription")

    # For paid tools (optional)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Monthly price in KES")
    stripe_price_id = models.CharField(max_length=100, blank=True, help_text="Stripe Price ID if using subscriptions")

    # Display order
    order = models.PositiveIntegerField(default=0, help_text="Display order")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.url
