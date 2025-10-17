from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'blogs'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Blog URLs
    path('', views.home_view, name='home'),
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blogs/create/', views.blog_create_view, name='blog_create'),
    path('blogs/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('blogs/<slug:slug>/edit/', views.blog_edit_view, name='blog_edit'),
    path('blogs/<slug:slug>/delete/', views.blog_delete_view, name='blog_delete'),
    path('blogs/<slug:slug>/like/', views.like_blog_view, name='like_blog'),
    
    # User's own blog posts
    path('my-blogs/', views.my_blog_list_view, name='my_blog_list'),
    
    # Category and Tag URLs
    path('categories/', views.category_list_view, name='category_list'),
    path('tags/', views.tag_list_view, name='tag_list'),
]
