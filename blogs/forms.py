from django import forms
from django.contrib.auth.models import User
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    """
    Comprehensive Django form for blog creation and editing.
    Includes proper validation and user-friendly fields.
    """
    
    class Meta:
        model = BlogPost
        fields = ['title', 'excerpt', 'content', 'tags', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your blog title...',
                'maxlength': 200
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a short description of your blog post...',
                'rows': 3,
                'maxlength': 300
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your blog content here...',
                'rows': 15
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas (e.g., python, django, web-development)',
                'maxlength': 200
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': 'Blog Title',
            'excerpt': 'Short Description',
            'content': 'Blog Content',
            'tags': 'Tags',
            'status': 'Publish Status'
        }
        help_texts = {
            'title': 'Choose a compelling title for your blog post (max 200 characters)',
            'excerpt': 'Provide a brief summary of your blog post (max 300 characters)',
            'content': 'Write your main blog content here. Be creative and informative!',
            'tags': 'Add relevant tags separated by commas to help readers find your post',
            'status': 'Choose whether to save as draft or publish immediately'
        }

    def clean_title(self):
        """
        Validate blog title to ensure it's not empty and meets requirements.
        """
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 5:
            raise forms.ValidationError("Blog title must be at least 5 characters long.")
        return title.strip()

    def clean_content(self):
        """
        Validate blog content to ensure it meets minimum requirements.
        """
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) < 50:
            raise forms.ValidationError("Blog content must be at least 50 characters long.")
        return content.strip()

    def clean_tags(self):
        """
        Clean and validate tags input.
        """
        tags = self.cleaned_data.get('tags')
        if tags:
            # Remove extra whitespace and convert to lowercase
            cleaned_tags = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
            # Remove duplicates while preserving order
            unique_tags = list(dict.fromkeys(cleaned_tags))
            return ', '.join(unique_tags)
        return tags

    def clean_excerpt(self):
        """
        Clean excerpt field.
        """
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt:
            return excerpt.strip()
        return excerpt


class BlogSearchForm(forms.Form):
    """
    Form for searching and filtering blog posts.
    """
    
    SEARCH_CHOICES = [
        ('title', 'Search by Title'),
        ('content', 'Search by Content'),
        ('author', 'Search by Author'),
        ('tags', 'Search by Tags'),
    ]
    
    STATUS_CHOICES = [
        ('', 'All Posts'),
        ('published', 'Published Only'),
        ('draft', 'Draft Only'),
    ]
    
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter search term...'
        }),
        label='Search Query'
    )
    
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Search In',
        initial='title'
    )
    
    status_filter = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Post Status',
        required=False,
        initial=''
    )
    
    tags = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by tags (comma-separated)...'
        }),
        label='Filter by Tags'
    )


class BlogCommentForm(forms.Form):
    """
    Form for adding comments to blog posts.
    """
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name...'
        }),
        label='Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        }),
        label='Email'
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write your comment here...',
            'rows': 4
        }),
        label='Comment'
    )
    
    def clean_name(self):
        """
        Validate name field.
        """
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        return name.strip()
    
    def clean_comment(self):
        """
        Validate comment field.
        """
        comment = self.cleaned_data.get('comment')
        if not comment or len(comment.strip()) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        return comment.strip()
