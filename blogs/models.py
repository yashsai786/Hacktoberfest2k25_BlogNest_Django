from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(10, message="Title must be at least 10 characters long."),
            MaxLengthValidator(200, message="Title cannot exceed 200 characters.")
        ],
        help_text="Enter a descriptive title for your blog post (10-200 characters)"
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title (auto-generated if left blank)"
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(100, message="Content must be at least 100 characters long.")
        ],
        help_text="Write your blog post content (minimum 100 characters)"
    )
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary of your blog post (optional, max 500 characters)"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='blog_posts',
        help_text="Select a category for your blog post"
    )
    tags = models.ManyToManyField(
        Tag, 
        blank=True,
        related_name='blog_posts',
        help_text="Select relevant tags for your blog post"
    )
    featured_image = models.ImageField(
        upload_to='blog_images/',
        blank=True,
        null=True,
        help_text="Upload a featured image for your blog post (optional)"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Choose the publication status"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark this post as featured"
    )
    allow_comments = models.BooleanField(
        default=True,
        help_text="Allow readers to comment on this post"
    )
    likes = models.IntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status != 'published':
            self.published_at = None
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])