from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import BlogPost, Category, Tag


class BlogPostForm(forms.ModelForm):
    """
    Comprehensive form for creating and editing blog posts with proper validation
    and user-friendly fields.
    """
    
    # Custom fields for better user experience
    new_category = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter new category name',
            'class': 'form-control'
        }),
        help_text="Create a new category (optional)"
    )
    
    new_tags = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter tags separated by commas (e.g., python, django, web)',
            'class': 'form-control'
        }),
        help_text="Enter tags separated by commas"
    )
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'content', 'excerpt', 'category', 'tags',
            'featured_image', 'status', 'is_featured', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a compelling title for your blog post',
                'maxlength': '200'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL-friendly version (auto-generated if left blank)',
                'maxlength': '250'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your blog post content here...',
                'style': 'resize: vertical;'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of your blog post (optional)',
                'maxlength': '500',
                'style': 'resize: vertical;'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'title': 'Enter a descriptive title for your blog post (10-200 characters)',
            'slug': 'URL-friendly version of the title (auto-generated if left blank)',
            'content': 'Write your blog post content (minimum 100 characters)',
            'excerpt': 'Brief summary of your blog post (optional, max 500 characters)',
            'category': 'Select a category for your blog post',
            'tags': 'Select relevant tags for your blog post',
            'featured_image': 'Upload a featured image for your blog post (optional)',
            'status': 'Choose the publication status',
            'is_featured': 'Mark this post as featured',
            'allow_comments': 'Allow readers to comment on this post'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up querysets for foreign key fields
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['tags'].queryset = Tag.objects.all().order_by('name')
        
        # Make slug field optional for new posts
        if not self.instance.pk:
            self.fields['slug'].required = False
        
        # Add Bootstrap classes for better styling
        for field_name, field in self.fields.items():
            if field_name not in ['is_featured', 'allow_comments']:
                if hasattr(field.widget, 'attrs'):
                    field.widget.attrs.update({'class': 'form-control'})
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Title is required.")
        
        # Check for minimum length
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")
        
        # Check for maximum length
        if len(title) > 200:
            raise ValidationError("Title cannot exceed 200 characters.")
        
        # Check for duplicate titles (excluding current instance)
        existing_posts = BlogPost.objects.filter(title__iexact=title)
        if self.instance.pk:
            existing_posts = existing_posts.exclude(pk=self.instance.pk)
        
        if existing_posts.exists():
            raise ValidationError("A blog post with this title already exists.")
        
        return title
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content:
            raise ValidationError("Content is required.")
        
        # Check for minimum length
        if len(content) < 100:
            raise ValidationError("Content must be at least 100 characters long.")
        
        return content
    
    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt')
        if excerpt and len(excerpt) > 500:
            raise ValidationError("Excerpt cannot exceed 500 characters.")
        return excerpt
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            # Auto-generate slug from title
            title = self.cleaned_data.get('title')
            if title:
                slug = slugify(title)
        
        if slug:
            # Check for duplicate slugs (excluding current instance)
            existing_posts = BlogPost.objects.filter(slug=slug)
            if self.instance.pk:
                existing_posts = existing_posts.exclude(pk=self.instance.pk)
            
            if existing_posts.exists():
                # Add a number suffix to make it unique
                counter = 1
                original_slug = slug
                while existing_posts.exists():
                    slug = f"{original_slug}-{counter}"
                    existing_posts = BlogPost.objects.filter(slug=slug)
                    if self.instance.pk:
                        existing_posts = existing_posts.exclude(pk=self.instance.pk)
                    counter += 1
        
        return slug
    
    def clean_new_category(self):
        new_category = self.cleaned_data.get('new_category')
        if new_category:
            # Check if category already exists
            if Category.objects.filter(name__iexact=new_category).exists():
                raise ValidationError("A category with this name already exists.")
        return new_category
    
    def clean_new_tags(self):
        new_tags = self.cleaned_data.get('new_tags')
        if new_tags:
            # Split by comma and clean up
            tag_names = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
            if len(tag_names) > 10:
                raise ValidationError("You can add at most 10 tags at once.")
            
            # Check for duplicate tags
            existing_tags = Tag.objects.filter(name__in=[tag.lower() for tag in tag_names])
            if existing_tags.exists():
                existing_names = [tag.name for tag in existing_tags]
                raise ValidationError(f"These tags already exist: {', '.join(existing_names)}")
        
        return new_tags
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that either category is selected or new category is provided
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        
        if not category and not new_category:
            self.add_error('category', 'Please select a category or create a new one.')
        
        # Validate featured image file size (max 5MB)
        featured_image = cleaned_data.get('featured_image')
        if featured_image and hasattr(featured_image, 'size'):
            if featured_image.size > 5 * 1024 * 1024:  # 5MB
                self.add_error('featured_image', 'Image file size cannot exceed 5MB.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the author
        if self.user:
            instance.author = self.user
        
        # Handle new category creation
        new_category = self.cleaned_data.get('new_category')
        if new_category and not instance.category:
            category, created = Category.objects.get_or_create(
                name=new_category,
                defaults={'description': f'Category for {new_category} posts'}
            )
            instance.category = category
        
        if commit:
            instance.save()
            # Save many-to-many relationships after the instance is saved
            self.save_m2m()
            
            # Handle new tags creation after the instance is saved
            new_tags = self.cleaned_data.get('new_tags')
            if new_tags:
                tag_names = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                    instance.tags.add(tag)
        
        return instance


class BlogPostSearchForm(forms.Form):
    """
    Form for searching blog posts
    """
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search blog posts...',
            'maxlength': '100'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '5'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Status'),
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing categories
    """
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'maxlength': '50'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description (optional)',
                'style': 'resize: vertical;'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for duplicate names (excluding current instance)
            existing_categories = Category.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing_categories = existing_categories.exclude(pk=self.instance.pk)
            
            if existing_categories.exists():
                raise ValidationError("A category with this name already exists.")
        
        return name


class TagForm(forms.ModelForm):
    """
    Form for creating and editing tags
    """
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tag name',
                'maxlength': '30'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.lower().strip()
            # Check for duplicate names (excluding current instance)
            existing_tags = Tag.objects.filter(name=name)
            if self.instance.pk:
                existing_tags = existing_tags.exclude(pk=self.instance.pk)
            
            if existing_tags.exists():
                raise ValidationError("A tag with this name already exists.")
        
        return name
