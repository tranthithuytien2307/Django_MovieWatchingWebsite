from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
import pandas as pd
import pickle
import requests
import os
import uuid
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from .models import AppUser, UserToken
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from decouple import config
from .models import Movie, Genre, Country

# Lấy API key từ môi trường (hoặc ghi thẳng để test)
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "YOUR_TMDB_API_KEY")

movies = pd.read_csv("models/movies.csv")
tfidf_matrix = pickle.load(open("models/tfidf_matrix.pkl", "rb"))
cosine_sim = pickle.load(open("models/cosine_sim.pkl", "rb"))
svd_model = pickle.load(open("models/svd_model.pkl", "rb"))

GOOGLE_CLIENT_ID = config("CLIENT_ID")
GOOGLE_CLIENT_SECRET = config("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/google/callback/"

# ===== Trang chủ (index) =====
def index(request):
    return render(request, "recommender/index.html")  

def google_login(request):
    """Redirect sang Google để login"""
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return redirect(google_auth_url)


def google_callback(request):
    """Xử lý code từ Google, tạo user + phát JWT"""
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    # Đổi code sang access_token từ Google
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    r = requests.post(token_url, data=token_data)
    token_json = r.json()

    if "error" in token_json:
        return JsonResponse({"error": token_json}, status=400)

    google_access_token = token_json.get("access_token")
    google_refresh_token = token_json.get("refresh_token")
    expires_in = token_json.get("expires_in", 3600)

    # Lấy thông tin user từ Google
    user_info = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {google_access_token}"},
    ).json()

    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    # Tạo hoặc lấy user
    user, created = AppUser.objects.get_or_create(
        email=email,
        defaults={
            "name": name,
            "avatar": picture,
            "phone": str(uuid.uuid4())[:10],  # tạm tạo số điện thoại random
        },
    )

    # Lưu Google token vào bảng UserToken
    UserToken.objects.create(
        user=user,
        access_token=google_access_token,
        refresh_token=google_refresh_token,
        access_expires_at=datetime.now() + timedelta(seconds=expires_in),
    )

    # Tạo JWT (access + refresh)
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    request.session['user'] = {
        'email': user.email,
        'name': user.name,
        'avatar': user.avatar
    }
    request.session['google_access_token'] = google_access_token
    request.session['google_refresh_token'] = google_refresh_token

    return redirect('index')

@api_view(["POST"])
def refresh_jwt(request):
    """
    Nhận refresh token từ client, trả về access token mới.
    """
    refresh_token = request.data.get("refresh_token")
    if not refresh_token:
        return Response({"error": "Missing refresh_token"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Tạo đối tượng RefreshToken từ token client gửi lên
        refresh = RefreshToken(refresh_token)

        # Sinh access token mới
        new_access_token = str(refresh.access_token)

        return Response({
            "access_token": new_access_token,
            "expires_in": 15 * 60,  # 15 phút
        })

    except TokenError:
        # Token không hợp lệ hoặc đã hết hạn
        return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("admin_dashboard")  # đăng nhập thành công -> về trang index
        else:
            return render(request, "recommender/login.html", {"error": "Email hoặc mật khẩu không đúng"})
    return render(request, "recommender/login.html")

# ===== Tìm phim theo query =====
def search_movie(request):
    query = request.GET.get('q', '').strip().lower()
    if not query:
        return JsonResponse([], safe=False)

    results = movies[movies['title'].str.lower().str.contains(query)]
    top_titles = list(results['title'].head(10))
    return JsonResponse(top_titles, safe=False)

# ===== Gợi ý phim =====
def recommend(request):
    query = request.GET.get("movie", "").strip()

    movies_qs = Movie.objects.all().values(
        "id", "name", "description", "release_year", "rating", "views", "poster"
    )
    movies_df = pd.DataFrame(list(movies_qs))

    if movies_df.empty:
        return render(request, "recommender/index.html", {
            "error": "Chưa có dữ liệu phim.",
            "query": query,
            "search_results": None,
            "trending_movies": Movie.objects.order_by("-views")[:5],
            "genres": Genre.objects.all(),
            "countries": Country.objects.all(),
        })

    if not query:
        # Không nhập gì -> hiện trang chủ
        return render(request, "recommender/index.html", {
            "movie_sections": {
                "Phim mới cập nhật": Movie.objects.order_by("-release_year")[:10],
                "Phim hot": Movie.objects.order_by("-views")[:10],
            },
            "trending_movies": Movie.objects.order_by("-views")[:5],
            "genres": Genre.objects.all(),
            "countries": Country.objects.all(),
        })

    # ✅ Build combined_features
    movies_df["combined_features"] = (
        movies_df["name"].fillna("") + " " +
        movies_df["description"].fillna("")
    )

    # Tìm phim trong DB
    matched = movies_df[movies_df["name"].str.contains(query, case=False, na=False)]
    if matched.empty:
        return render(request, "recommender/index.html", {
            "error": f'Không tìm thấy phim "{query}".',
            "query": query,
            "search_results": None,
            "trending_movies": Movie.objects.order_by("-views")[:5],
            "genres": Genre.objects.all(),
            "countries": Country.objects.all(),
        })

    # Có kết quả
    idx = matched.index[0]
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(movies_df["combined_features"])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]

    recommendations = movies_df.iloc[movie_indices][["name", "poster", "description"]].to_dict(orient="records")

    return render(request, "recommender/index.html", {
        "search_results": recommendations,
        "query": query,
        "trending_movies": Movie.objects.order_by("-views")[:5],
        "genres": Genre.objects.all(),
        "countries": Country.objects.all(),
    })


# ===== Lấy poster + mô tả từ TMDb =====
def get_movie_info(title):
    try:
        r = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": TMDB_API_KEY, "query": title}
        )
        r.raise_for_status()
        data = r.json()
        results = data.get('results')
        if results:
            movie = results[0]
            poster_path = movie.get("poster_path")
            overview = movie.get("overview", "")
            return {
                "poster": f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None,
                "overview": overview
            }
    except Exception as e:
        print(f"Error fetching movie info: {e}")
    return {"poster": None, "overview": ""}

from django.db.models import Q

from django.db.models import Q

def index(request):
    query = request.GET.get("q", "").strip()
    genre_id = request.GET.get("genre")
    country_id = request.GET.get("country")
    year = request.GET.get("year")

    search_results = None
    error = None
    movie_sections = None  # mặc định None để phân biệt với giao diện trang chủ

    # Nếu có query hoặc filter thì search
    if query or genre_id or country_id or year:
        movies = Movie.objects.all()

        if query:
            movies = movies.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if genre_id:
            movies = movies.filter(genres__id=genre_id)

        if country_id:
            movies = movies.filter(country__id=country_id)

        if year:
            movies = movies.filter(release_year=year)

        search_results = movies.distinct()

        if not search_results.exists():
            error = f'Không tìm thấy phim phù hợp với "{query}".'
    else:
        # Không có query/filter -> hiển thị trang chủ
        movie_sections = {
            "Phim mới cập nhật": Movie.objects.order_by("-release_year")[:10],
            "Phim hot": Movie.objects.order_by("-views")[:10],
        }

    # Trending (top views)
    trending_movies = Movie.objects.order_by("-views")[:5]

    context = {
        "query": query,
        "search_results": search_results,
        "error": error,
        "trending_movies": trending_movies,
        "movie_sections": movie_sections,
        "genres": Genre.objects.all(),
        "countries": Country.objects.all(),
    }
    return render(request, "recommender/index.html", context)