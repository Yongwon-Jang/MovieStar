from django.db import models
from django.conf import settings

class Genre(models.Model):
    genre_no = models.IntegerField()
    genre_name = models.CharField(max_length=20)

class Movie(models.Model):
    movie_id = models.IntegerField()
    title = models.CharField(max_length=100)
    original_title = models.CharField(max_length=100)
    release_date = models.DateField()
    popularity = models.FloatField(null=True, blank=True)
    vote_count = models.IntegerField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    poster_path = models.CharField(max_length=200)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users_like')
    hate_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='users_hate')
    add_movie = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='movie_add')
    click = models.IntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, blank=True, related_name='movies')
    language = models.CharField(max_length=30)


class LineReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()