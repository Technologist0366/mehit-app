from django.urls import path
from . import views

app_name = 'policies'

urlpatterns = [
    # HTML pages
    path('questionnaire/', views.questionnaire, name='questionnaire'),
    path('<slug:slug>/', views.policy_detail, name='detail'),          # user's own policy

    # API endpoints
    path('api/generate/', views.generate_policy, name='generate'),
    path('api/list/', views.list_policies, name='list'),
    path('api/public/<slug:slug>/', views.public_policy, name='public'),
]
