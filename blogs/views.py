from django.shortcuts import render
from .models import User, BlogPost


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        User.objects.create_user(username=username, password=password)
        return render(request, 'signup_success.html')
    return render(request, 'signup.html')


