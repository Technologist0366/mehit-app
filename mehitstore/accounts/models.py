import uuid
import os  # <-- added missing import for profile_photo_path
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

def profile_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profiles', str(instance.id), filename)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Login fields
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, blank=True, null=True)  # optional
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(regex=r'^(\+254|0)[0-9]{9}$', message='Enter a valid Kenyan phone number')]
    )

    # OAuth (optional)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    facebook_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    auth_provider = models.CharField(max_length=50, default='email', choices=[
        ('email', 'Email/Password'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ])

    # Personal info
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_photo = models.ImageField(upload_to=profile_photo_path, null=True, blank=True)

    # Business info
    company_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=50, blank=True, choices=[
        ('INDIVIDUAL', 'Individual'),
        ('SME', 'Small Business'),
        ('SACCO', 'SACCO'),
        ('SCHOOL', 'School'),
        ('CLINIC', 'Clinic'),
        ('FINANCE', 'Financial Services'),
        ('NGO', 'Non-Profit'),
        ('OTHER', 'Other'),
    ])

    # Kenya‑specific
    kra_pin = models.CharField(max_length=50, blank=True)
    business_reg = models.CharField(max_length=100, blank=True)

    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    # Payment defaults
    default_payment_method = models.CharField(max_length=20, choices=[
        ('MPESA', 'M-PESA'),
        ('WALLET', 'Platform Wallet'),
        ('CARD', 'Credit/Debit Card'),
    ], default='MPESA')

    default_mpesa_phone = models.CharField(max_length=15, blank=True)
    auto_pay_enabled = models.BooleanField(default=False)
    auto_pay_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_email = models.EmailField(blank=True, help_text="Where to send payment receipts")

    # Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    # Preferences
    preferred_language = models.CharField(max_length=10, choices=[
        ('en', 'English'),
        ('sw', 'Swahili'),
    ], default='en')

    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)

    # Security
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)

    # ===== FIX: Add these two fields to resolve reverse accessor clashes =====
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="accounts_user_set",
        related_query_name="accounts_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="accounts_user_set",
        related_query_name="accounts_user",
    )
    # ===== END FIX =====

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['company_name']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.company_name:
            return self.company_name
        return self.email.split('@')[0]

    @property
    def initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[:2].upper()
        elif self.company_name:
            return self.company_name[:2].upper()
        return self.email[:2].upper()

    @property
    def profile_completion_percentage(self):
        fields = [
            bool(self.phone_number),
            bool(self.first_name),
            bool(self.last_name),
            bool(self.address),
            bool(self.city),
            bool(self.company_name),
            self.email_verified,
            self.phone_verified,
            bool(self.default_mpesa_phone),
        ]
        return int((sum(fields) / len(fields)) * 100)

    def get_missing_fields_for_checkout(self):
        missing = []
        if not self.phone_number:
            missing.append({'field': 'phone', 'message': 'Phone number needed for delivery', 'url': '/accounts/profile/edit/#phone'})
        elif not self.phone_verified:
            missing.append({'field': 'verify_phone', 'message': 'Verify phone to receive order updates', 'url': '/accounts/verify-phone/'})
        if not self.address:
            missing.append({'field': 'address', 'message': 'Delivery address needed', 'url': '/accounts/profile/edit/#address'})
        if not self.city:
            missing.append({'field': 'city', 'message': 'City needed for delivery', 'url': '/accounts/profile/edit/#city'})
        return missing

    def get_missing_fields_for_subscription(self):
        missing = []
        if not self.company_name:
            missing.append({'field': 'company', 'message': 'Company name needed for billing', 'url': '/accounts/profile/edit/#company'})
        if not self.kra_pin and self.business_type != 'INDIVIDUAL':
            missing.append({'field': 'kra_pin', 'message': 'KRA PIN needed for invoice', 'url': '/accounts/profile/edit/#kra'})
        if not self.billing_email:
            missing.append({'field': 'billing_email', 'message': 'Billing email needed for receipts', 'url': '/accounts/profile/edit/#billing'})
        return missing

    def verify_phone(self):
        self.phone_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['phone_verified', 'verified_at'])

    def verify_email(self):
        self.email_verified = True
        self.save(update_fields=['email_verified'])

    def update_last_active(self):
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def record_login(self, request):
        self.last_login = timezone.now()
        self.last_login_ip = self.get_client_ip(request)
        self.login_attempts = 0
        self.save(update_fields=['last_login', 'last_login_ip', 'login_attempts'])

    def failed_login(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save(update_fields=['login_attempts', 'locked_until'])

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class UserPaymentMethod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')

    METHOD_TYPES = [
        ('MPESA', 'M-PESA'),
        ('WALLET', 'Platform Wallet'),
        ('CARD', 'Credit/Debit Card'),
    ]
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)

    mpesa_phone = models.CharField(max_length=15, blank=True, validators=[RegexValidator(regex=r'^(\+254|0)[0-9]{9}$')])
    mpesa_verified = models.BooleanField(default=False)
    mpesa_verified_at = models.DateTimeField(null=True, blank=True)

    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)
    card_expiry = models.CharField(max_length=7, blank=True)

    wallet_address = models.CharField(max_length=255, blank=True)

    display_name = models.CharField(max_length=100, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    last_used = models.DateTimeField(null=True, blank=True)
    used_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-last_used']
        unique_together = ['user', 'mpesa_phone']
        indexes = [models.Index(fields=['user', 'is_default']), models.Index(fields=['mpesa_phone'])]

    def __str__(self):
        if self.method_type == 'MPESA':
            return f"M-PESA: {self.mpesa_phone}"
        elif self.method_type == 'CARD':
            return f"{self.card_brand}: ****{self.card_last4}"
        return f"Wallet: {self.wallet_address[:10]}..."

    @property
    def display(self):
        if self.display_name:
            return self.display_name
        if self.method_type == 'MPESA':
            return f"M-PESA {self.mpesa_phone}"
        elif self.method_type == 'CARD':
            return f"{self.card_brand} ****{self.card_last4}"
        return "Wallet"

    def use(self):
        self.last_used = timezone.now()
        self.used_count += 1
        self.save(update_fields=['last_used', 'used_count'])

    def save(self, *args, **kwargs):
        if self.is_default:
            UserPaymentMethod.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class UserTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')

    SERVICE_TYPES = [
        ('STORE', 'Store Purchase'),
        ('CMP', 'CMP Subscription'),
        ('SAAS', 'SaaS Subscription'),
        ('WALLET', 'Wallet Top-up'),
    ]
    service = models.CharField(max_length=20, choices=SERVICE_TYPES, db_index=True)
    service_ref = models.CharField(max_length=100, blank=True, db_index=True)

    payment_method = models.ForeignKey(UserPaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    mpesa_receipt = models.CharField(max_length=100, blank=True, db_index=True)
    mpesa_checkout_id = models.CharField(max_length=100, blank=True)

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'service']),
            models.Index(fields=['mpesa_receipt']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.service} - KES {self.amount}"

    def mark_completed(self, mpesa_receipt=None):
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if mpesa_receipt:
            self.mpesa_receipt = mpesa_receipt
        self.save(update_fields=['status', 'completed_at', 'mpesa_receipt'])


class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')

    device_id = models.CharField(max_length=255, db_index=True)
    device_name = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=50, choices=[
        ('MOBILE', 'Mobile'),
        ('TABLET', 'Tablet'),
        ('DESKTOP', 'Desktop'),
        ('UNKNOWN', 'Unknown'),
    ], default='UNKNOWN')

    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    location_city = models.CharField(max_length=100, blank=True)
    location_country = models.CharField(max_length=100, blank=True)

    is_trusted = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_login']
        indexes = [models.Index(fields=['user', 'device_id']), models.Index(fields=['last_login'])]

    def __str__(self):
        return f"{self.device_name or self.device_type} - {self.last_login.date()}"


class UserLoginHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')

    login_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_id = models.CharField(max_length=255, blank=True)

    successful = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-login_time']
        indexes = [models.Index(fields=['user', 'login_time']), models.Index(fields=['ip_address'])]

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"
