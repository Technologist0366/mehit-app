from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, UserPaymentMethod, UserTransaction, UserDevice, UserLoginHistory

class UserPaymentMethodInline(admin.TabularInline):
    model = UserPaymentMethod
    extra = 0
    readonly_fields = ['created_at', 'last_used']

class UserTransactionInline(admin.TabularInline):
    model = UserTransaction
    extra = 0
    readonly_fields = ['created_at', 'completed_at']

class UserDeviceInline(admin.TabularInline):
    model = UserDevice
    extra = 0
    readonly_fields = ['last_login', 'created_at']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'full_name_display', 'phone_number', 'company_name', 'verification_badge', 'is_active', 'created_at_display']
    list_filter = ['is_active', 'email_verified', 'phone_verified', 'business_type', 'auth_provider']
    search_fields = ['email', 'phone_number', 'company_name', 'first_name', 'last_name']

    # Define custom fieldsets by extending the default UserAdmin fieldsets
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'profile_photo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Kenyan Business Info', {
            'fields': ('company_name', 'business_type', 'kra_pin', 'business_reg', 'address', 'city', 'county', 'postal_code')
        }),
        ('Verification', {
            'fields': ('email_verified', 'phone_verified', 'verified_at')
        }),
        ('Payment Settings', {
            'fields': ('default_payment_method', 'default_mpesa_phone', 'auto_pay_enabled', 'auto_pay_threshold', 'billing_email')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'email_notifications', 'sms_notifications', 'marketing_consent')
        }),
        ('Security', {
            'fields': ('last_login_ip', 'login_attempts', 'locked_until')
        }),
        ('OAuth', {
            'fields': ('google_id', 'facebook_id', 'auth_provider')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_active'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_active', 'last_login', 'date_joined', 'login_attempts']
    inlines = [UserPaymentMethodInline, UserTransactionInline, UserDeviceInline]

    actions = ['verify_emails', 'verify_phones', 'unlock_accounts']

    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Name'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d')
    created_at_display.short_description = 'Joined'

    def verification_badge(self, obj):
        if obj.email_verified and obj.phone_verified:
            return format_html('<span style="color:green;">✅ Fully Verified</span>')
        elif obj.email_verified:
            return format_html('<span style="color:orange;">📧 Email Only</span>')
        elif obj.phone_verified:
            return format_html('<span style="color:orange;">📱 Phone Only</span>')
        return format_html('<span style="color:red;">❌ Not Verified</span>')
    verification_badge.short_description = 'Verification'

    def verify_emails(self, request, queryset):
        queryset.update(email_verified=True)
    verify_emails.short_description = "Mark emails as verified"

    def verify_phones(self, request, queryset):
        queryset.update(phone_verified=True, verified_at=timezone.now())
    verify_phones.short_description = "Mark phones as verified"

    def unlock_accounts(self, request, queryset):
        queryset.update(locked_until=None, login_attempts=0)
    unlock_accounts.short_description = "Unlock selected accounts"


@admin.register(UserPaymentMethod)
class UserPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'method_type', 'display', 'is_default', 'is_active', 'last_used']
    list_filter = ['method_type', 'is_default', 'is_active', 'mpesa_verified']
    search_fields = ['user__email', 'mpesa_phone']
    readonly_fields = ['created_at', 'updated_at', 'last_used']


@admin.register(UserTransaction)
class UserTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'amount', 'status', 'mpesa_receipt', 'created_at']
    list_filter = ['service', 'status', 'created_at']
    search_fields = ['user__email', 'mpesa_receipt', 'service_ref']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'ip_address', 'successful']
    list_filter = ['successful', 'login_time']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['login_time', 'ip_address', 'user_agent']
