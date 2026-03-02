from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import BlogPost, Category, Tag, SourceOrganization
import json

@require_GET
def api_posts(request):
    """API endpoint for blog posts with filtering and pagination"""
    posts = BlogPost.objects.all().select_related('category', 'source', 'author').prefetch_related('tags')
    
    # Apply filters
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    source_id = request.GET.get('source')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    if source_id:
        posts = posts.filter(source_id=source_id)
    
    if status:
        posts = posts.filter(status=status)
    else:
        # Default to showing published posts only
        posts = posts.filter(status='published')
    
    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(excerpt__icontains=search) |
            Q(content__icontains=search)
        )
    
    # Order by most recent
    posts = posts.order_by('-published_at', '-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 9))
    paginator = Paginator(posts, page_size)
    posts_page = paginator.get_page(page)
    
    # Format response
    results = []
    for post in posts_page:
        # Get tags
        tags = [{'name': tag.name, 'slug': tag.slug} for tag in post.tags.all()]
        
        # Get author name
        author_name = None
        if post.author:
            author_name = post.author.get_full_name() or post.author.username
        
        results.append({
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'content': post.content[:200] + '...' if post.content else '',
            'featured_image': post.featured_image.url if post.featured_image else None,
            'category_name': post.category.name if post.category else None,
            'category_slug': post.category.slug if post.category else None,
            'source_name': post.source.name if post.source else None,
            'source_id': post.source.id if post.source else None,
            'author_name': author_name,
            'tags': tags,
            'status': post.status,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'created_at': post.created_at.isoformat(),
            'meta_title': post.meta_title,
            'meta_description': post.meta_description,
        })
    
    return JsonResponse({
        'results': results,
        'count': paginator.count,
        'current_page': posts_page.number,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
    })

@require_GET
def api_categories(request):
    """API endpoint for categories with post counts"""
    categories = Category.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).order_by('name')
    
    data = [{
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'post_count': cat.post_count,
    } for cat in categories]
    
    return JsonResponse(data, safe=False)

@require_GET
def api_tags(request):
    """API endpoint for tags with post counts"""
    tags = Tag.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).order_by('name')
    
    data = [{
        'id': tag.id,
        'name': tag.name,
        'slug': tag.slug,
        'post_count': tag.post_count,
    } for tag in tags]
    
    return JsonResponse(data, safe=False)

@require_GET
def api_sources(request):
    """API endpoint for source organizations with post counts"""
    sources = SourceOrganization.objects.annotate(
        post_count=Count('blogpost', filter=Q(blogpost__status='published'))
    ).order_by('name')
    
    data = [{
        'id': source.id,
        'name': source.name,
        'website': source.website,
        'rss_feed': source.rss_feed,
        'post_count': source.post_count,
    } for source in sources]
    
    return JsonResponse(data, safe=False)

@require_GET
def api_stats(request):
    """API endpoint for blog statistics"""
    total_posts = BlogPost.objects.filter(status='published').count()
    total_authors = BlogPost.objects.filter(status='published').values('author').distinct().count()
    total_sources = SourceOrganization.objects.filter(blogpost__status='published').distinct().count()
    total_categories = Category.objects.filter(blogpost__status='published').distinct().count()
    
    return JsonResponse({
        'total_posts': total_posts,
        'total_authors': total_authors,
        'total_sources': total_sources,
        'total_categories': total_categories,
    })

@require_GET
def api_post_detail(request, category_slug, slug):
    """API endpoint for single blog post detail"""
    try:
        post = BlogPost.objects.select_related('category', 'source', 'author').prefetch_related('tags').get(
            slug=slug,
            category__slug=category_slug
        )
        
        # Get tags
        tags = [{'name': tag.name, 'slug': tag.slug} for tag in post.tags.all()]
        
        # Get author name
        author_name = None
        if post.author:
            author_name = post.author.get_full_name() or post.author.username
        
        data = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'content': post.content,
            'featured_image': post.featured_image.url if post.featured_image else None,
            'category_name': post.category.name if post.category else None,
            'category_slug': post.category.slug if post.category else None,
            'source_name': post.source.name if post.source else None,
            'source_id': post.source.id if post.source else None,
            'source_website': post.source.website if post.source else None,
            'source_url': post.source_url,
            'author_name': author_name,
            'tags': tags,
            'status': post.status,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
            'meta_title': post.meta_title,
            'meta_description': post.meta_description,
        }
        
        return JsonResponse(data)
        
    except BlogPost.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

@csrf_exempt
def api_newsletter_subscribe(request):
    """API endpoint for newsletter subscription"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({'error': 'Email is required'}, status=400)
            
            # Here you would typically save to a NewsletterSubscriber model
            # For now, we'll just return success
            return JsonResponse({
                'success': True,
                'message': 'Successfully subscribed to newsletter'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)