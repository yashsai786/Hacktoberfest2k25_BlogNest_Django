from django.db import models

# for simplification, we will use default user model provided by django auth
from django.contrib.auth.models import User


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.CharField(max_length=300, blank=True, help_text="Short description of the blog post")
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    likes = models.IntegerField(default=0)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title