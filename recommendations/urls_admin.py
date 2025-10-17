from django.urls import path
from . import views_admin

urlpatterns = [
    path("movies/", views_admin.movie_admin_list, name="movie_admin_list"),
    path("movies/<uuid:pk>/", views_admin.movie_detail, name="movie_detail"),
    path('movie/<uuid:movie_id>/watch/', views_admin.watch_movie, name='watch_movie'),
    path("movies/<uuid:movie_id>/episode/<uuid:episode_id>/", views_admin.watch_episode, name="watch_episode"),
    path("movies/add/", views_admin.movie_create, name="movie_create"),
    path("movies/<uuid:pk>/edit/", views_admin.movie_update, name="movie_update"),
    path("movies/<uuid:pk>/delete/", views_admin.movie_delete, name="movie_delete"),
    path("", views_admin.admin_dashboard, name="admin_dashboard"),
    path("users/", views_admin.users_list, name="users_list"),
    path("users/<uuid:pk>/", views_admin.user_detail, name="user_detail"),
    path("directors/", views_admin.director_admin_list, name="director_admin_list"),
    path("directors/create/", views_admin.director_admin_create, name="director_create"),
    path("directors/<uuid:pk>/", views_admin.director_admin_detail, name="director_detail"),
    path("directors/<uuid:pk>/update/", views_admin.director_admin_update, name="director_update"),
    path("directors/<uuid:pk>/delete/", views_admin.director_admin_delete, name="director_delete"),
]
