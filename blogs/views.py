from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from .models import User, BlogPost, Category, Tag
from .forms import BlogPostForm, BlogPostSearchForm, CategoryForm, TagForm


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        User.objects.create_user(username=username, password=password)
        return render(request, 'signup_success.html')
    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth_views.authenticate(request, username=username, password=password)
        if user is not None:
            auth_views.login(request, user)
            return render(request, 'home.html')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def home_view(request):
    posts = BlogPost.objects.filter(status='published').order_by('-created_at')[:6]
    return render(request, 'home.html', {'posts': posts})


@login_required
def blog_create_view(request):
    """
    View for creating a new blog post
    """
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            blog_post = form.save()
            messages.success(request, f'Blog post "{blog_post.title}" has been created successfully!')
            return redirect('blog_detail', slug=blog_post.slug)
    else:
        form = BlogPostForm(user=request.user)
    
    return render(request, 'blogs/blog_form.html', {'form': form})


@login_required
def blog_edit_view(request, slug):
    """
    View for editing an existing blog post
    """
    blog_post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=blog_post, user=request.user)
        if form.is_valid():
            blog_post = form.save()
            messages.success(request, f'Blog post "{blog_post.title}" has been updated successfully!')
            return redirect('blog_detail', slug=blog_post.slug)
    else:
        form = BlogPostForm(instance=blog_post, user=request.user)
    
    return render(request, 'blogs/blog_form.html', {'form': form, 'blog_post': blog_post})


def blog_detail_view(request, slug):
    """
    View for displaying a single blog post
    """
    blog_post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    blog_post.increment_views()
    
    return render(request, 'blogs/blog_detail.html', {'blog_post': blog_post})


def blog_list_view(request):
    """
    View for listing all published blog posts with search and filter functionality
    """
    posts = BlogPost.objects.filter(status='published').order_by('-created_at')
    
    # Search functionality
    search_form = BlogPostSearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        tags = search_form.cleaned_data.get('tags')
        status = search_form.cleaned_data.get('status')
        is_featured = search_form.cleaned_data.get('is_featured')
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) | 
                Q(excerpt__icontains=query)
            )
        
        if category:
            posts = posts.filter(category=category)
        
        if tags:
            posts = posts.filter(tags__in=tags).distinct()
        
        if status:
            posts = posts.filter(status=status)
        
        if is_featured:
            posts = posts.filter(is_featured=True)
    
    # Pagination
    paginator = Paginator(posts, 9)  # Show 9 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for filter dropdowns
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'blogs/blog_list.html', context)


@login_required
def my_blog_list_view(request):
    """
    View for listing user's own blog posts
    """
    posts = BlogPost.objects.filter(author=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blogs/my_blog_list.html', {'page_obj': page_obj})


@login_required
def blog_delete_view(request, slug):
    """
    View for deleting a blog post
    """
    blog_post = get_object_or_404(BlogPost, slug=slug, author=request.user)
    
    if request.method == 'POST':
        title = blog_post.title
        blog_post.delete()
        messages.success(request, f'Blog post "{title}" has been deleted successfully!')
        return redirect('my_blog_list')
    
    return render(request, 'blogs/blog_confirm_delete.html', {'blog_post': blog_post})


def category_list_view(request):
    """
    View for listing all categories
    """
    categories = Category.objects.all().order_by('name')
    return render(request, 'blogs/category_list.html', {'categories': categories})


def tag_list_view(request):
    """
    View for listing all tags
    """
    tags = Tag.objects.all().order_by('name')
    return render(request, 'blogs/tag_list.html', {'tags': tags})


@login_required
def like_blog_view(request, slug):
    """
    AJAX view for liking a blog post
    """
    if request.method == 'POST':
        blog_post = get_object_or_404(BlogPost, slug=slug)
        blog_post.likes += 1
        blog_post.save()
        return JsonResponse({'likes': blog_post.likes})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
