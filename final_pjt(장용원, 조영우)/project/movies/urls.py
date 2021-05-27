from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('<str:genre_name>/genre_recommended', views.genre_recommended, name='genre_recommended'),
    path('<int:movie_id>/linereview/', views.create_linereview, name='create_linereview'),
    path('<int:movie_id>/<int:linereview_pk>/linereview_delete/', views.delete_linereview, name='delete_linereview'),
    path('<int:movie_id>/like/', views.like, name='like'),
    path('<int:movie_id>/hate/', views.hate, name='hate'),
    path('<int:movie_id>/add_movie/', views.add_movie, name='add_movie'),
    path('search/', views.search, name='search'),
]