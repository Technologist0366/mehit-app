from django.db import models  # Add this import for Count and Q
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import BlogPost, Category, Tag, SourceOrganization
from django.http import HttpResponse



def blog_list(request):
    """HTML view for blog listing page"""
    # Get all published posts
    posts = BlogPost.objects.filter(status='published').order_by('-published_at', '-created_at')
    
    # Get filter parameters
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    source_id = request.GET.get('source')
    search_query = request.GET.get('search')
    
    # Apply filters
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    if source_id:
        posts = posts.filter(source_id=source_id)
    if search_query:
        posts = posts.filter(title__icontains=search_query)
    
    # Pagination
    paginator = Paginator(posts, 9)  # Show 9 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get sidebar data
    categories = Category.objects.annotate(
        post_count=models.Count('blogpost', filter=models.Q(blogpost__status='published'))
    ).order_by('name')
    
    tags = Tag.objects.annotate(
        post_count=models.Count('blogpost', filter=models.Q(blogpost__status='published'))
    ).order_by('name')
    
    sources = SourceOrganization.objects.annotate(
        post_count=models.Count('blogpost', filter=models.Q(blogpost__status='published'))
    ).order_by('name')
    
    recent_posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'tags': tags,
        'sources': sources,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, category_slug, slug):
    """HTML view for single blog post"""
    post = get_object_or_404(
        BlogPost, 
        slug=slug, 
        category__slug=category_slug,
        status='published'
    )
    
    # Get related posts (same category, exclude current)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(id=post.id)[:3]
    
    # Get tags
    tags = post.tags.all()
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'tags': tags,
    }
    return render(request, 'blog/blog_detail.html', context)

def blog_category(request, category_slug):
    """View for posts in a specific category"""
    category = get_object_or_404(Category, slug=category_slug)
    posts = BlogPost.objects.filter(
        category=category, 
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_category.html', context)

def blog_tag(request, tag_slug):
    """View for posts with a specific tag"""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = BlogPost.objects.filter(
        tags=tag, 
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_tag.html', context)

def blog_source(request, source_id):
    """View for posts from a specific source"""
    source = get_object_or_404(SourceOrganization, id=source_id)
    posts = BlogPost.objects.filter(
        source=source, 
        status='published'
    ).order_by('-published_at')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'source': source,
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_source.html', context)


def debug_headers(request):
    """Debug view to show request headers"""
    headers = "<h1>Request Headers</h1><pre>"
    for key, value in request.META.items():
        if key.startswith('HTTP_'):
            headers += f"{key}: {value}\n"
    headers += "</pre>"
    headers += f"<h2>Request details:</h2><pre>"
    headers += f"path: {request.path}\n"
    headers += f"method: {request.method}\n"
    headers += f"GET: {request.GET}\n"
    headers += f"POST: {request.POST}\n"
    headers += f"COOKIES: {request.COOKIES}\n"
    headers += f"request.META['SERVER_NAME']: {request.META.get('SERVER_NAME', 'Not set')}\n"
    headers += f"request.META['SERVER_PORT']: {request.META.get('SERVER_PORT', 'Not set')}\n"
    headers += f"request.META['REMOTE_ADDR']: {request.META.get('REMOTE_ADDR', 'Not set')}\n"
    headers += "</pre>"
    return HttpResponse(headers)

def home(request):
    """Homepage view serving index.html with latest blog posts"""
    # Get the 3 most recent published blog posts
    latest_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('category').order_by('-published_at')[:3]
    
    context = {
        'latest_posts': latest_posts,
    }
    return render(request, 'index.html', context)
