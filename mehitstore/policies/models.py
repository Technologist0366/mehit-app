import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

def policy_pdf_path(instance, filename):
    return f"policies/{instance.user.id}/{instance.slug}/policy.pdf"

def policy_qr_path(instance, filename):
    return f"policies/{instance.user.id}/{instance.slug}/qr.png"

class PolicyTemplate(models.Model):
    """Stores the HTML template for the privacy policy."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_structure = models.JSONField(help_text="Must contain 'html' key with the template")
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

class Policy(models.Model):
    """Generated policy for a user."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='policies')
    template = models.ForeignKey(PolicyTemplate, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    responses = models.JSONField(default=dict)          # all answers from the form
    generated_content = models.TextField(blank=True)    # final HTML
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    effective_date = models.DateField(default=timezone.now)
    pdf_file = models.FileField(upload_to=policy_pdf_path, null=True, blank=True)
    qr_code = models.ImageField(upload_to=policy_qr_path, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"policy-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
