from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Review, Comment
from movies.models import Movie
import requests

from .forms import ReviewForm, CommentForm, SearchForm
from django.http import JsonResponse, HttpResponse


from decouple import config
api_key = config('api_key')# Create your views here.
############################################################################################################
# 커뮤니티 홈페이지
@require_http_methods(['GET', 'POST'])
@login_required
def index(request):
    if request.method == 'POST':
        reviews = Review.objects.all()
        post = request.POST.get('post', '')
        if post:
            reviews =reviews.filter(movie_title__icontains=post)
        context = {
            'reviews' : reviews,
            'post' : post,
        }
    else:
        reviews = Review.objects.order_by('pk')
        context = {
            'reviews': reviews,
        }
    return render(request, 'community/index.html', context)

############################################################################################################
# 게시글 생성
@require_http_methods(['GET', 'POST'])
@login_required
def create(request, movie_id):
############################################################################################################# 영화상세정보 받기
    Detail_URL =  f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR'
    Detail_res = requests.get(Detail_URL)
    Detail_data = Detail_res.json()
    # 없다면 모델에 저장해주기~
    if  (not Movie.objects.filter(movie_id=Detail_data.get('id')).exists()) and (Detail_data.get('release_date')):
        Movie.objects.get_or_create(
            movie_id = Detail_data.get('id'),
            title = Detail_data.get('title'),
            original_title = Detail_data.get('original_title'),
            release_date = Detail_data.get('release_date'),
            popularity = Detail_data.get('popularity'),
            vote_count = Detail_data.get('vote_count'),
            vote_average = Detail_data.get('vote_average'),
            overview = Detail_data.get('overview'),
            poster_path = f'https://image.tmdb.org/t/p/w500/{Detail_data.get("poster_path")}',
            click = Detail_data.get('vote_count'),
            language=Detail_data.get('original_language'),
        )
    movie = get_object_or_404(Movie, movie_id=movie_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie_title = movie.title
            review.movie_id = movie.movie_id
            review.save()
            return redirect('community:detail', review.pk)
    else:
        form = ReviewForm()
    context = {
        'form': form,
        'movie': movie,
        
    }
    return render(request, 'community/create.html', context)

############################################################################################################
# 게시글 디테일
@require_http_methods(['GET', 'POST'])
@login_required
def detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comments = review.comment_set.all()
    comment_form = CommentForm()
    review_user = review.user
    movie_id = review.movie_id
    if not (review.click):
        review.click = 0
    review.click += 1
    review.save()
    context = {
        'review': review,
        'comment_form': comment_form,
        'comments': comments,
        'review_user' : review_user,
        'movie_id' : movie_id,
    }
    return render(request, 'community/detail.html', context)

############################################################################################################
# 게시글 수정
@require_http_methods(['GET', 'POST'])
def update(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('community:detail', review.pk)
    else:
        form = ReviewForm(instance=review)
    context = {
        'form': form,
        'review': review,
    }
    return render(request, 'community/update.html', context)

############################################################################################################
# 게시글 삭제
@require_POST
def delete(request, review_pk):
    review = get_object_or_404(Review, id=review_pk)
    review.delete()
    return redirect('community:index')

############################################################################################################
# 댓글 생성
@require_POST
def create_comment(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.review = review
        comment.user = request.user
        comment.save()
        return redirect('community:detail', review.pk)
    context = {
        'comment_form': comment_form,
        'review': review,
        'comments': review.comment_set.all(),
    }
    return render(request, 'community/detail.html', context)

############################################################################################################
# 댓글삭제
@require_POST
def comment_delete(request, review_pk, comment_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment = get_object_or_404(Comment, id=comment_pk)
    comment.delete()
    return redirect('community:detail', review.pk)

############################################################################################################
# 게시글 좋아요
@require_POST
def like(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        user = request.user

        if review.like_users.filter(pk=user.pk).exists():
            review.like_users.remove(user)
            liked = False
        else:
            review.like_users.add(user)
            liked = True

        response_data={
            'liked':liked,
            'count':review.like_users.count(),
        }
        return JsonResponse(response_data)
    return HttpResponse(status=401)

############################################################################################################
#  게시글 싫어요
@require_POST
def hate(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        user = request.user

        if review.hate_users.filter(pk=user.pk).exists():
            review.hate_users.remove(user)
            hated = False
        else:
            review.hate_users.add(user)
            hated = True

        response_data={
            'hated':hated,
            'count':review.hate_users.count(),
        }
        return JsonResponse(response_data)
    return HttpResponse(status=401)