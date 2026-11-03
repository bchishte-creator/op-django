from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = 'tracker'

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit, name='submit'),
    path('search/', views.search, name='search'),
    path('food-pictures/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='tracker/login.html',
            redirect_authenticated_user=True,
            next_page='tracker:home',
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page=reverse_lazy('tracker:login')),
        name='logout',
    ),
]
