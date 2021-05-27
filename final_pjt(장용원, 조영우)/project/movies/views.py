from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import Genre, LineReview, Movie
from .forms import LineReviewForm
import requests
from django.contrib.auth.decorators import login_required
from community.models import Review
from django.http import JsonResponse, HttpResponse
import datetime
import random

# Create your views here.
###############################################API_KEY받기###############################################
from decouple import config
api_key = config('api_key')

###############################################movies메인페이지###############################################
@login_required
@require_GET
def index(request):
    ###############################################장르 넣어주기###############################################
    GENRE_URL = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=ko-KR'
    genre_res = requests.get(GENRE_URL)
    genre_data = genre_res.json().get('genres')
    for i in genre_data:
        if not Genre.objects.filter(genre_no=i.get('id')).exists():
            Genre.objects.get_or_create(
                genre_no = i.get('id'),
                genre_name = i.get('name')
            )
    ###############################################영화 먼저 넣어두기(데이터 없을때만)###############################################
    movies = Movie.objects.all()
    if len(movies) == 0:
        for page in range(1,6):
            Movie_base_URL = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&language=ko-KR&sort_by=popularity.desc&include_adult=false&include_video=false&page={page}&with_watch_monetization_types=flatrate'
            movie_res = requests.get(Movie_base_URL)
            movie_data = movie_res.json().get('results')
            for i in movie_data:
                if (i.get('release_date')):
                    Movie.objects.get_or_create(
                        movie_id = i.get('id'),
                        title = i.get('title'),
                        original_title = i.get('original_title'),
                        release_date = i.get('release_date'),
                        popularity = i.get('popularity'),
                        vote_count = i.get('vote_count'),
                        vote_average = i.get('vote_average'),
                        overview = i.get('overview'),
                        poster_path = f'https://image.tmdb.org/t/p/w500/{i.get("poster_path")}',
                        click = i.get('vote_count'),
                        language=i.get('original_language'),
                    )
                    temp = Movie.objects.get(movie_id=i.get('id'))
                    temp_genres = i.get('genre_ids')
                    for genre in temp_genres:
                        temp_genre = Genre.objects.get(genre_no=genre)
                        temp.genres.add(temp_genre)

    ###############################################d조회순###############################################
    movie_list = Movie.objects.order_by('-click')[:6]
    ###############################################popular###############################################
    popular_movie_list=Movie.objects.order_by('-popularity')[:6]
    ###############################################top_rated영화정보###############################################
    top_movie_data=Movie.objects.order_by('-vote_count')[:6]
    ###############################################내가 좋아요한 영화 기반으로 추천###############################################
    my_like_list = list((request.user.users_like.values('movie_id'))) # 좋아요한 영화목록들(번호로 들어가있음)
    movies_id_list = [] # 영화id가져오기
    for i in my_like_list: 
        movies_id_list.append(i['movie_id'])
    # 좋아요한 영화들의 장르모임
    movies_genres_list = []
    for j in movies_id_list:
        movie = Movie.objects.get(movie_id=j)
        genres  = movie.genres.all()
        for k in genres:
            if not k.id in movies_genres_list:
                movies_genres_list.append(k.id)
    movies_genre_list=[]
    for i in movies_genres_list:
        movies_genre_list.extend(Movie.objects.filter(genres=i))
    
    temp = set(movies_genre_list)

    if len(temp) > 6:
        recommend_to_user = random.sample(temp, 6)
    else:
        recommend_to_user = temp


    context = {
        'movie_list':movie_list,
        'popular_movie_list':popular_movie_list,
        'top_movie_data':top_movie_data,
        'recommend_to_user':recommend_to_user,
    }
    
    return render(request, 'movies/index.html', context)

############################################################################################################
## 영화 상세페이지에서는 movie_id를 받자마자 detail로 탐색 후 모델에 저장해서 사용하게된다.
@login_required
@require_GET
def detail(request, movie_id):
###############################################영화상세조회###############################################
    Detail_URL =  f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=ko-KR'
    Detail_res = requests.get(Detail_URL)
    Detail_data = Detail_res.json()
    # 없다면 모델에 저장해주기~
    if (not Movie.objects.filter(movie_id=movie_id).exists()) and(Detail_data.get('release_date')):
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
###############################################영화id를받아서 그다음 movie에 저장한 다음에 사용해보자.###############################################
    movie = get_object_or_404(Movie, movie_id=movie_id)

###############################################장르정보받기###############################################
    movie_genres = Detail_data.get('genres')
    movie_genres_id = []
    for i in range(len(movie_genres)):
        movie_genres_id.append(movie_genres[i]['id'])

    for genre in movie_genres_id:
        temp = Genre.objects.get(genre_no=genre)
        movie.genres.add(temp)
        
    movie_genres_list = movie.genres.all()


###############################################영화아이디받기
    moId = movie.movie_id
###############################################비디오정보받기
    video = Detail_data["video"]

###############################################현재영화정보로 랜덤으로 추천받기###############################################
    Recomen_URL = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={api_key}&language=ko-KR&page=1'
    Now_Recomen_res = requests.get(Recomen_URL)
    Now_Recomen_data = Now_Recomen_res.json().get('results')
    Now_recomen_movie_list = []
############################################### 12개보다 이상이면, 12개만 넣고
    if len(Now_Recomen_data) > 12:
        for i in range(12):
            Now_recomen_movie_list.append(Now_Recomen_data[i])
############################################### 12개보다 미만이면, 다 넣고
    else:
        for i in Now_Recomen_data:
            Now_recomen_movie_list.append(i)

    

###############################################해당 영화에 대한 리뷰들###############################################
    reviews = Review.objects.filter(movie_title=movie.title)
###############################################한줄리뷰###############################################
    linereviews = movie.linereview_set.all()
###############################################한줄리뷰form###############################################
    linereview_form=LineReviewForm()

###############################################평점계산###############################################
    # 현재 평점
    now_rating = movie.vote_average
    # 평가 참여자수
    now_voted = movie.vote_count
    # 평점의 총 합(나누기전)
    sum_rating = (now_rating)*(now_voted)
    #이 영화에 리뷰를 쓴 사람들의 수(한줄리뷰+노말리뷰)
    rate_users = len(linereviews)+len(reviews)
    # 평가참여자수+영화리뷰쓴사람들의 수
    new_rating_people = now_voted+rate_users
    # 새롭게 평가한 사람들의 점수(한줄리뷰의점수+노말리뷰의점수)
    new_rating = 0
    for i in linereviews:
        new_rating+=i.rating
    for i in reviews:
        new_rating+i.rank
    # 평점의 합
    new_sum_rating = sum_rating+new_rating
    # 최종평점
    if new_rating_people !=0:
        Real_rating = round(new_sum_rating/new_rating_people,2)
    else:
        Real_rating = 0
    # 저장
    movie.vote_average = Real_rating
    movie.vote_count = new_rating_people # 기존에 더한거라 바로 넣어주는거임)
###############################################조회수(디테일에들어오면 조회했다는 의미로간주해서 기본click은 투표자수+들어오면+1)###############################################
    movie.click += 1
    movie.save() # 저장

    context = {
        'movie':movie, # 저장된 영화정보
        'Now_recomen_movie_list':Now_recomen_movie_list, # 현재 추천 영화 리스트(자동)
        'reviews':reviews, # 리뷰들
        'video':video, # 비디오
        'linereviews':linereviews, # 한줄평들
        'linereview_form':linereview_form, # 한줄평 Form
        # 'new_rating_people':new_rating_people, # 
        'Real_rating':Real_rating, # 반영된 리뷰
        'moId':moId, # id계산안되길래 넣어준아이
        'movie_genres_list':movie_genres_list, # 장르리스트
    }
    return render(request, 'movies/detail.html', context)

############################################### 한줄 리뷰 만들기 ###############################################
@login_required
@require_POST
def create_linereview(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    linereview_form = LineReviewForm(request.POST)
    # movierating_form = MovieRatingForm(request.POST)
    rating = request.POST.get('rating')

    if linereview_form.is_valid():
        # 한줄리뷰
        linereview = linereview_form.save(commit=False)
        linereview.movie = movie
        linereview.user = request.user
        linereview.rating = int(rating)
        linereview.save()

        return redirect('movies:detail', movie_id)

    context = {
        'linereview_form': linereview_form,
        'movie': movie,
    }
    return render(request, 'movies/detail.html', context, movie_id)

###############################################
# 한줄 리뷰 삭제
@login_required
@require_POST
def delete_linereview(request, movie_id, linereview_pk):
    movie = get_object_or_404(Movie, movie_id=movie_id)
    linereview = get_object_or_404(LineReview, pk=linereview_pk)
    linereview.delete()
    return redirect('movies:detail', movie_id)

###############################################
# 영화 좋아요
@login_required
@require_POST
def like(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, movie_id=movie_id)
        user = request.user

        if movie.like_users.filter(pk=user.pk).exists():
            movie.like_users.remove(user)
            liked = False
        else:
            movie.like_users.add(user)
            liked = True

        response_data={
            'liked':liked,
            'count':movie.like_users.count(),
        }
        return JsonResponse(response_data)
    return HttpResponse(status=401)

###############################################
# 영화 싫어요
@require_POST
def hate(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, movie_id=movie_id)
        user = request.user

        if movie.hate_users.filter(pk=user.pk).exists():
            movie.hate_users.remove(user)
            hated = False
        else:
            movie.hate_users.add(user)
            hated = True

        response_data={
            'hated':hated,
            'count':movie.hate_users.count(),
        }
        return JsonResponse(response_data)
    return HttpResponse(status=401)

###############################################
# 영화 찜
@require_POST
def add_movie(request, movie_id):
    if request.user.is_authenticated:
        movie = get_object_or_404(Movie, movie_id=movie_id)
        user = request.user

        if movie.add_movie.filter(pk=user.pk).exists():
            movie.add_movie.remove(user)
            added_movie = False
        else:
            movie.add_movie.add(user)
            added_movie = True

        response_data={
            'added_movie':added_movie,
            'count':movie.add_movie.count(),
        }
        return JsonResponse(response_data)
    return HttpResponse(status=401)

###############################################
# 영화검색
@require_GET
def search(request):
    search_movie = request.GET.get('search')
    searched_result_movies = []
    for page in range(1,5):
        URL_SEARCH = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=ko-KR&query={search_movie}&page={page}&include_adult=false'
        searched_movie_res = requests.get(URL_SEARCH)
        searched_movie_data = searched_movie_res.json().get('results')
        for i in searched_movie_data:
            if  Movie.objects.filter(movie_id=i.get('id')).exists():
                searched_result_movies.append(i)
            elif  (not Movie.objects.filter(movie_id=i.get('id')).exists()) and (i.get('release_date')):
                Movie.objects.get_or_create(
                    movie_id = i.get('id'),
                    title = i.get('title'),
                    original_title = i.get('original_title'),
                    release_date = i.get('release_date'),
                    popularity = i.get('popularity'),
                    vote_count = i.get('vote_count'),
                    vote_average = i.get('vote_average'),
                    overview = i.get('overview'),
                    poster_path = f'https://image.tmdb.org/t/p/w500/{i.get("poster_path")}',
                    click = i.get('vote_count'),
                    language=i.get('original_language'),
                )
                temp = Movie.objects.get(movie_id=i.get('id'))
                temp_genres = i.get('genre_ids')
                for genre in temp_genres:
                    temp_genre = Genre.objects.get(genre_no=genre)
                    temp.genres.add(temp_genre)
            
                searched_result_movies.append(i)

    context = {
        'searched_result_movies' : searched_result_movies,
    }
    return render(request, 'movies/search.html', context)

###############################################
# 영화장르로 검색

# movies_genre_list=[]
#     for i in movies_genres_list:
#         movies_genre_list.extend(Movie.objects.filter(genres=i))


def genre_recommended(request, genre_name):
    genre= genre_name
    genre_no = Genre.objects.get(genre_name=genre).id # 장르아이디
    ############################################### 날짜
    now = datetime.date.today().isoformat()
    ############################################### 장르별 + 인기순
    genre_popular = Movie.objects.filter(genres=genre_no).order_by('-popularity')[:6]
    if len(genre_popular) == 0:
        genre_popular=[]
    ############################################### 장르별 + 평가 많이 참여한순
    genre_vote = Movie.objects.filter(genres=genre_no).order_by('-vote_count')[:6]
    if len(genre_vote) == 0:
        genre_vote=[]
    ############################################### 장르별 + 출시순
    genre_date = Movie.objects.filter(genres=genre_no).order_by('-release_date')[:6]
    if len(genre_date) == 0:
        genre_date=[]
    ############################################### 장르별 + 한국인기순
    genre_click = Movie.objects.filter(genres=genre_no).order_by('-click')[:6]
    if len(genre_click) == 0:
        genre_click=[]
    ############################################### 장르별 + 언어가 영어
    en_movie = Movie.objects.filter(genres=genre_no,language='en').order_by('-popularity')[:6]
    if len(en_movie) == 0:
        en_movie=[]
    ############################################### 장르별 + 언어가 한국어
    ko_movie = Movie.objects.filter(genres=genre_no,language='ko').order_by('-popularity')[:6]
    if len(ko_movie) == 0:
        ko_movie=[]
    ############################################### 장르별 + 일본인기순
    jp_movie = Movie.objects.filter(genres=genre_no,language='ja').order_by('-popularity')[:6]
    if len(jp_movie) == 0:
        jp_movie=[]
    ############################################### 장르별 + 중국인기순
    zh_movie = Movie.objects.filter(genres=genre_no,language='zh').order_by('-popularity')[:6]
    if len(zh_movie) == 0:
        zh_movie=[]

    context={
        'genre': genre,
        'genre_no':genre_no,
        'genre_popular':genre_popular,
        'genre_vote':genre_vote,
        'genre_date':genre_date,
        'genre_click':genre_click,
        'en_movie':en_movie,
        'ko_movie':ko_movie,
        'jp_movie':jp_movie,
        'zh_movie':zh_movie,
    }
    return render(request, 'movies/genre_recommended.html', context)