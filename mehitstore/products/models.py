# apps/products/models.py
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """
    Product categories (e.g. Fire Safety, PPE, Electrical Safety, Inspection Tools)
    """
    name = models.CharField(
        _("Name"),
        max_length=100,
        unique=True,
        help_text=_("e.g. Fire Safety, PPE, Compliance Kits")
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=120,
        unique=True,
        blank=True,
        help_text=_("Auto-generated from name")
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Optional short description shown on category pages")
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_("Uncheck to hide this category from the storefront")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Core product model for safety & compliance equipment
    """
    sku = models.CharField(
        _("SKU"),
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Unique stock-keeping unit (e.g. FS-EXT-6KG)")
    )
    name = models.CharField(
        _("Product Name"),
        max_length=255,
        help_text=_("e.g. ABC Fire Extinguisher – 6kg")
    )
    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("Auto-generated from name for clean URLs")
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("Category"),
        help_text=_("Main category this product belongs to")
    )
    price = models.DecimalField(
        _("Price (KES)"),
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text=_("Selling price in Kenyan Shillings")
    )
    description = models.TextField(
        _("Full Description"),
        blank=True,
        help_text=_("Detailed product description (supports HTML)")
    )
    key_features = models.JSONField(
        _("Key Features"),
        default=list,
        blank=True,
        help_text=_("List of bullet points, e.g. ['KEBS certified', '5-year warranty']")
    )
    specifications = models.JSONField(
        _("Technical Specifications"),
        default=dict,
        blank=True,
        help_text=_("Key-value pairs, e.g. {'Weight': '8.5kg', 'Dimensions': 'Φ180 × H500mm'}")
    )
    image = models.ImageField(
        _("Main Product Image"),
        upload_to='products/images/%Y/%m/',
        blank=True,
        null=True,
        help_text=_("Primary photo shown in catalog and detail page")
    )
    datasheet = models.FileField(
        _("Datasheet / Technical Document"),
        upload_to='products/datasheets/%Y/%m/',
        blank=True,
        null=True,
        help_text=_("PDF, PNG, JPG, DOCX etc. — max 10MB recommended")
    )
    stock = models.PositiveIntegerField(
        _("Stock Quantity"),
        default=10,
        help_text=_("Current physical stock level")
    )
    is_active = models.BooleanField(
        _("Active / Visible"),
        default=True,
        help_text=_("Uncheck to hide from storefront without deleting")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def image_url(self):
        """Safe URL for templates/API"""
        return self.image.url if self.image else None

    @property
    def datasheet_url(self):
        """Safe URL for templates/API"""
        return self.datasheet.url if self.datasheet else None

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def low_stock(self):
        return 0 < self.stock <= 5