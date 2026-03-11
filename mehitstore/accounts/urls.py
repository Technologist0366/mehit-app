from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Phone verification
    path('verify-phone/', views.verify_phone, name='verify_phone'),

    # Payment methods
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('payment-methods/add/', views.payment_methods, name='add_payment_method'),
    path('payment-methods/<uuid:method_id>/verify/', views.verify_payment_method, name='verify_payment_method'),
    path('payment-methods/<uuid:method_id>/default/', views.set_default_payment, name='set_default_payment'),
    path('payment-methods/<uuid:method_id>/delete/', views.delete_payment_method, name='delete_payment_method'),

    # Transactions
    path('transactions/', views.transaction_history, name='transaction_history'),

    # Password reset (optional – using Django's built-in views)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
