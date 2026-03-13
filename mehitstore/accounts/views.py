import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Sum
from .models import User, UserPaymentMethod, UserTransaction
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, PaymentMethodForm, VerifyPhoneForm
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    if request.user.is_authenticated:
        return redirect('tools')  # redirect to tools page
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Account created successfully!")
            return redirect('/tools/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('tools')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            if user.locked_until and user.locked_until > timezone.now():
                messages.error(request, f"Account locked. Try again after {user.locked_until.strftime('%H:%M')}")
                return render(request, 'registration/login.html', {'form': form})
            login(request, user)
            user.record_login(request)
            UserLoginHistory.objects.create(user=user, ip_address=user.get_client_ip(request), user_agent=request.META.get('HTTP_USER_AGENT', ''), successful=True)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect(request.GET.get('next', 'tools'))
        else:
            try:
                login_input = request.POST.get('login')
                user = User.objects.filter(email=login_input).first() or User.objects.filter(phone_number=login_input).first()
                if user:
                    user.failed_login()
            except:
                pass
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out")
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    total_transactions = UserTransaction.objects.filter(user=user).count()
    total_spent = UserTransaction.objects.filter(user=user, status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0
    recent_transactions = UserTransaction.objects.filter(user=user)[:5]
    payment_methods = user.payment_methods.filter(is_active=True)
    return render(request, 'accounts/profile.html', {
        'user': user,
        'total_transactions': total_transactions,
        'total_spent': total_spent,
        'recent_transactions': recent_transactions,
        'payment_methods': payment_methods,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def payment_methods(request):
    payment_methods = request.user.payment_methods.filter(is_active=True)
    transactions = UserTransaction.objects.filter(user=request.user)[:10]
    total_spent = transactions.filter(status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            method = form.save(commit=False)
            method.user = request.user
            method.save()
            if method.method_type == 'MPESA':
                send_verification_code(method.mpesa_phone)
                messages.info(request, f"Verification code sent to {method.mpesa_phone}")
                return redirect('accounts:verify_payment_method', method_id=method.id)
            messages.success(request, "Payment method added successfully")
            return redirect('accounts:payment_methods')
    else:
        form = PaymentMethodForm()
    return render(request, 'accounts/payment_methods.html', {
        'payment_methods': payment_methods,
        'transactions': transactions,
        'total_spent': total_spent,
        'form': form,
    })

@login_required
def verify_payment_method(request, method_id):
    method = get_object_or_404(UserPaymentMethod, id=method_id, user=request.user)
    if method.mpesa_verified:
        messages.info(request, "This payment method is already verified")
        return redirect('accounts:payment_methods')
    if request.method == 'POST':
        form = VerifyPhoneForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f'verify_mpesa_{method.mpesa_phone}')
            if code == cached_code:
                method.mpesa_verified = True
                method.mpesa_verified_at = timezone.now()
                method.save()
                if not request.user.payment_methods.filter(is_default=True).exists():
                    method.is_default = True
                    method.save()
                messages.success(request, "Payment method verified successfully!")
                return redirect('accounts:payment_methods')
            else:
                messages.error(request, "Invalid verification code")
    else:
        send_verification_code(method.mpesa_phone)
        form = VerifyPhoneForm()
    return render(request, 'accounts/verify_payment.html', {'method': method, 'form': form})

@login_required
def set_default_payment(request, method_id):
    method = get_object_or_404(UserPaymentMethod, id=method_id, user=request.user)
    request.user.default_payment_method = method.method_type
    if method.method_type == 'MPESA':
        request.user.default_mpesa_phone = method.mpesa_phone
    request.user.save()
    method.is_default = True
    method.save()
    messages.success(request, f"{method.display} set as default payment method")
    return redirect('accounts:payment_methods')

@login_required
def delete_payment_method(request, method_id):
    method = get_object_or_404(UserPaymentMethod, id=method_id, user=request.user)
    method.is_active = False
    method.save()
    if method.is_default:
        request.user.default_payment_method = 'MPESA'
        request.user.default_mpesa_phone = ''
        request.user.save()
    messages.success(request, "Payment method removed")
    return redirect('accounts:payment_methods')

@login_required
def verify_phone(request):
    user = request.user
    if not user.phone_number:
        messages.warning(request, "Please add a phone number first")
        return redirect('accounts:edit_profile')
    if request.method == 'POST':
        form = VerifyPhoneForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            cached_code = cache.get(f'verify_phone_{user.phone_number}')
            if code == cached_code:
                user.verify_phone()
                messages.success(request, "Phone number verified successfully!")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Invalid verification code")
    else:
        send_verification_code(user.phone_number)
        form = VerifyPhoneForm()
    return render(request, 'accounts/verify_phone.html', {'form': form})

@login_required
def transaction_history(request):
    transactions = UserTransaction.objects.filter(user=request.user)
    service = request.GET.get('service')
    if service:
        transactions = transactions.filter(service=service)
    period = request.GET.get('period')
    if period == '30days':
        transactions = transactions.filter(created_at__gte=timezone.now() - timezone.timedelta(days=30))
    elif period == '90days':
        transactions = transactions.filter(created_at__gte=timezone.now() - timezone.timedelta(days=90))
    elif period == 'year':
        transactions = transactions.filter(created_at__gte=timezone.now() - timezone.timedelta(days=365))
    summary = {
        'STORE': transactions.filter(service='STORE', status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
        'CMP': transactions.filter(service='CMP', status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
        'SAAS': transactions.filter(service='SAAS', status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
        'WALLET': transactions.filter(service='WALLET', status='COMPLETED').aggregate(total=Sum('amount'))['total'] or 0,
    }
    return render(request, 'accounts/transaction_history.html', {
        'transactions': transactions,
        'summary': summary,
        'total': sum(summary.values()),
        'service_choices': UserTransaction.SERVICE_TYPES,
        'current_service': service,
        'current_period': period,
    })

# Helper functions
def send_verification_code(phone):
    code = str(random.randint(100000, 999999))
    cache.set(f'verify_mpesa_{phone}', code, timeout=300)
    print(f"🔐 Verification code for {phone}: {code}")  # Replace with actual SMS sending in production
    return code
