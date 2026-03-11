from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import User, UserPaymentMethod

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}))
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        validators=[RegexValidator(regex=r'^(\+254|0)[0-9]{9}$', message='Enter a valid Kenyan phone number')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XX XXX XXX (optional)'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    login = forms.CharField(label="Email or Phone", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com or 07XX XXX XXX'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    remember_me = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def clean(self):
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        if login and password:
            # Try email first
            try:
                user = User.objects.get(email=login)
                username = user.username
            except User.DoesNotExist:
                try:
                    user = User.objects.get(phone_number=login)
                    username = user.username
                except User.DoesNotExist:
                    username = login
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid login credentials")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive")
            cleaned_data['user'] = user
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'profile_photo',
            'company_name', 'business_type', 'kra_pin', 'business_reg',
            'address', 'city', 'county', 'postal_code',
            'preferred_language', 'email_notifications', 'sms_notifications', 'marketing_consent',
            'default_payment_method', 'default_mpesa_phone', 'auto_pay_enabled', 'auto_pay_threshold', 'billing_email',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = UserPaymentMethod
        fields = ['method_type', 'mpesa_phone', 'display_name', 'is_default']
        widgets = {
            'method_type': forms.Select(attrs={'class': 'form-select'}),
            'mpesa_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '07XX XXX XXX'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., My Safaricom'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_mpesa_phone(self):
        phone = self.cleaned_data.get('mpesa_phone')
        if phone:
            if not phone.startswith('0') and not phone.startswith('254'):
                raise forms.ValidationError("Phone must start with 0 or 254")
            phone = phone.replace(' ', '')
            if UserPaymentMethod.objects.filter(mpesa_phone=phone, is_active=True).exclude(id=self.instance.id if self.instance else None).exists():
                raise forms.ValidationError("This phone number is already registered")
        return phone


class VerifyPhoneForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '000000'}))
