from django.contrib import admin
from .models import BlogPost, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'created_at', 'views', 'likes']
    list_filter = ['status', 'is_featured', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'excerpt', 'author__username']
    list_editable = ['status', 'is_featured']
    ordering = ['-created_at']
    filter_horizontal = ['tags']
    readonly_fields = ['slug', 'created_at', 'updated_at', 'published_at', 'views', 'likes']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'author')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'allow_comments', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views', 'likes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')
