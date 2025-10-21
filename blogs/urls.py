from django.urls import path
from .views import signup_view, home_view, blog_create_view

app_name = 'blogs'


urlpatterns = [
    path('', home_view, name='home'),
    path('create/', blog_create_view, name='create'),
]
