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
    path("admin/users/create/", views_admin.user_create, name="user_create"),
    path("users/<uuid:pk>/edit/", views_admin.user_edit, name="user_edit"),
    path("users/<uuid:pk>/change-password/", views_admin.user_change_password, name="user_change_password"),
    path("users/<uuid:pk>/toggle-status/", views_admin.user_toggle_status, name="user_toggle_status"),

    path("directors/", views_admin.director_admin_list, name="director_admin_list"),
    path("directors/create/", views_admin.director_admin_create, name="director_create"),
    path("directors/<uuid:pk>/", views_admin.director_admin_detail, name="director_detail"),
    path("directors/<uuid:pk>/update/", views_admin.director_admin_update, name="director_update"),
    path("directors/<uuid:pk>/delete/", views_admin.director_admin_delete, name="director_delete"),

    path("actors/", views_admin.actor_list, name="actor_list"),
    path("actors/create/", views_admin.actor_create, name="actor_create"),
    path("actors/<uuid:actor_id>/", views_admin.actor_detail, name="actor_detail"),
    path("actors/<uuid:actor_id>/edit/", views_admin.actor_edit, name="actor_edit"),
    path("actors/<uuid:actor_id>/delete/", views_admin.actor_delete, name="actor_delete"),

    path('genre-country/', views_admin.genre_country_admin, name="genre_country_admin"),
    path('genre/add/', views_admin.genre_add, name="genre_add"),
    path('country/add/', views_admin.country_add, name="country_add"),
    path('genre/delete/<uuid:id>/', views_admin.genre_delete, name="genre_delete"),
    path('country/delete/<uuid:id>/', views_admin.country_delete, name="country_delete"),
    path('genre/edit/<uuid:id>/', views_admin.genre_edit, name='genre_edit'),
    path('country/edit/<uuid:id>/', views_admin.country_edit, name='country_edit'),

    path('reviews/', views_admin.review_admin_list, name='review_admin_list'),
    path('reviews/delete/<uuid:review_id>/', views_admin.review_delete, name='review_delete'),
]
