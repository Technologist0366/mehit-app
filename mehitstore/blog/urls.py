from django.urls import path
from . import views
from . import views_api

app_name = 'blog'

urlpatterns = [
    # API endpoints
    path('api/posts/', views_api.api_posts, name='api_posts'),
    path('api/categories/', views_api.api_categories, name='api_categories'),
    path('api/tags/', views_api.api_tags, name='api_tags'),
    path('api/sources/', views_api.api_sources, name='api_sources'),
    path('api/stats/', views_api.api_stats, name='api_stats'),
    path('api/newsletter/subscribe/', views_api.api_newsletter_subscribe, name='api_newsletter_subscribe'),
    path('api/<slug:category_slug>/<slug:slug>/', views_api.api_post_detail, name='api_post_detail'),
    
    # HTML views
    path('', views.blog_list, name='blog_list'),
    path('category/<slug:category_slug>/', views.blog_category, name='blog_category'),
    path('tag/<slug:tag_slug>/', views.blog_tag, name='blog_tag'),
    path('source/<int:source_id>/', views.blog_source, name='blog_source'),
    path('<slug:category_slug>/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('debug/', views.debug_headers, name='debug_headers'),
]
