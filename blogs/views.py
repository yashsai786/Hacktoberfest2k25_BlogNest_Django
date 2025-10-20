from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views.generic import CreateView, ListView

from .models import User, BlogPost
from .forms import BlogPostForm

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
    posts = BlogPost.objects.all()
    return render(request, 'home.html', {'posts': posts})
    

class BlogPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    
