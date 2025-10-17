from django.urls import path
from . import views, views_admin
from django.urls import path, include
from .views import google_login, google_callback


urlpatterns = [
    # User
    path('', views.index, name="index"),
    path('search/', views.search_movie, name="search_movie"),
    path('recommend/', views.recommend, name="recommend"),
    path('login/', views.login_page, name='login'),
    path("auth/google/login/", google_login, name="google-login"),
    path("auth/google/callback/", google_callback, name="google-callback"),
    path("auth/refresh/", views.refresh_jwt, name="token-refresh"),
]
