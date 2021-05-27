from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/create/', views.create, name='create'),
    path('<int:review_pk>/', views.detail, name='detail'),
    path('<int:review_pk>/update', views.update, name='update'),
    path('<int:review_pk>/delete', views.delete, name='delete'),
    path('<int:review_pk>/comments/', views.create_comment, name='create_comment'),
    path('<int:review_pk>/<int:comment_pk>/comment_delete/', views.comment_delete, name='comment_delete'),
    path('<int:review_pk>/like/', views.like, name='like'),
    path('<int:review_pk>/hate/', views.hate, name='hate'),
]