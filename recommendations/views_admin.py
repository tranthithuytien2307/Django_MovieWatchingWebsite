from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Director, Episode, Country
from .forms import MovieForm
from .models import AppUser, Genre
from .forms import DirectorForm
from urllib.parse import urlparse, parse_qs
from django.core.paginator import Paginator

# Trang dashboard admin
def admin_dashboard(request):
    stats = {
        "orders": 0,
        "movies": 0,
        "users": {"new": 0, "total": 27},
        "posts": {"new": 0, "total": 84},
    }
    revenue = [4000000, 3200000, 1000000]  # dữ liệu biểu đồ
    labels = ["Tháng 12/2023", "Tháng 1/2024", "Tháng 2/2024"]

    return render(request, "recommender/admin_dashboard.html", {
        "stats": stats,
        "revenue": revenue,
        "labels": labels
    })

# Trang user
def users_list(request):
    users = AppUser.objects.all()
    return render(request, "recommender/admin/users_list.html", {"users": users})

def user_detail(request, pk):
    user = get_object_or_404(AppUser, pk=pk)
    return render(request, "recommender/admin/user_detail.html", {"user": user})

def movie_admin_list(request):
    movie_list = Movie.objects.all().order_by('-id')  # mới nhất lên trước
    paginator = Paginator(movie_list, 10)  # 10 phim / trang

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "recommender/movie_admin_list.html", {"page_obj": page_obj})

def watch_episode(request, movie_id, episode_id):
    movie = get_object_or_404(Movie, id=movie_id)
    episode = get_object_or_404(Episode, id=episode_id, movie=movie)

    video_id = extract_video_id(episode.link) if episode.link else None

    embed_url = None
    watch_url = None
    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        watch_url = f"https://www.youtube.com/watch?v={video_id}"

    # vẫn truyền recommended_movies và trending_movies như watch_movie để UI đồng bộ
    recommended_movies = Movie.objects.filter(
        genres__in=movie.genres.all()
    ).exclude(id=movie.id).distinct()[:5]

    trending_movies = Movie.objects.order_by("-views", "-release_year")[:5]

    return render(
        request,
        "recommender/watch_movie.html",  # dùng lại template watch_movie
        {
            "movie": movie,
            "episode": episode,
            "video_id": video_id,
            "embed_url": embed_url,
            "watch_url": watch_url,
            "recommended_movies": recommended_movies,
            "trending_movies": trending_movies,
        },
    )


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    # Phim đề cử: cùng thể loại hoặc cùng diễn viên
    recommended_movies = Movie.objects.filter(
        genres__in=movie.genres.all()
    ).exclude(id=movie.id).distinct()[:5]

    # Top trending: phim mới + nhiều lượt xem
    trending_movies = Movie.objects.order_by("-views", "-release_year")[:5]

    return render(
        request,
        "recommender/movie_detail.html",
        {
            "movie": movie,
            "recommended_movies": recommended_movies,
            "trending_movies": trending_movies,
        },
    )


def extract_video_id(link: str) -> str | None:
    if not link:
        return None
    # Nếu đã là embed: https://www.youtube.com/embed/ID
    if "/embed/" in link:
        return link.rstrip("/").split("/")[-1]
    # Nếu là watch?v=ID
    parsed = urlparse(link)
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    # Nếu là share short link youtu.be/ID
    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    return None


def watch_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # Chống tăng view ảo (tăng 1 lần mỗi session)
    session_key = f"viewed_movie_{movie.id}"
    if not request.session.get(session_key, False):
        movie.views = movie.views + 1
        movie.save(update_fields=["views"])
        request.session[session_key] = True

    #  Xử lý link video
    video_id = extract_video_id(movie.trailer_link) if movie.trailer_link else None
    embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None
    watch_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None

    # Phim đề cử: cùng thể loại hoặc cùng diễn viên
    recommended_movies = (
        Movie.objects.filter(genres__in=movie.genres.all())
        .exclude(id=movie.id)
        .distinct()[:5]
    )

    # Phim trending: nhiều view + mới
    trending_movies = Movie.objects.order_by("-views", "-release_year")[:5]

    return render(
        request,
        "recommender/watch_movie.html",
        {
            "movie": movie,
            "video_id": video_id,
            "embed_url": embed_url,
            "watch_url": watch_url,
            "recommended_movies": recommended_movies,
            "trending_movies": trending_movies,
        },
    )

# Thêm phim
def movie_create(request):
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            # Lưu instance nhưng chưa commit vào DB
            movie = form.save(commit=False)

            # Xử lý Country
            new_country = request.POST.get("new_country")
            if new_country:
                country_obj, _ = Country.objects.get_or_create(name=new_country.strip())
                movie.country = country_obj

            # Xử lý Director
            new_director = request.POST.get("new_director")
            if new_director:
                director_obj, _ = Director.objects.get_or_create(name=new_director.strip())
                movie.director = director_obj

            movie.save()  # Lưu movie

            #  Lưu genres (ManyToMany)
            form.save_m2m()  # Lưu các genres đã chọn
            new_genres = request.POST.get("new_genres")
            if new_genres:
                for g in new_genres.split(","):
                    genre_obj, _ = Genre.objects.get_or_create(name=g.strip())
                    movie.genres.add(genre_obj)

            return redirect("movie_admin_list")
    else:
        form = MovieForm()
    return render(request, "recommender/movie_form.html", {"form": form})

# Sửa phim
def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            return redirect("movie_admin_list")
    else:
        form = MovieForm(instance=movie)
    return render(request, "recommender/movie_form.html", {"form": form})

# Xóa phim
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        movie.delete()
        return redirect("movie_admin_list")
    return render(request, "recommender/movie_confirm_delete.html", {"movie": movie})
#Danh sách đạo diễn
def director_admin_list(request):
    directors_list = Director.objects.all().order_by("name")
    paginator = Paginator(directors_list, 10)  # 10 đạo diễn / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "recommender/directors/director_admin_list.html", {"page_obj": page_obj})


def director_admin_create(request):
    if request.method == "POST":
        form = DirectorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("director_admin_list")
    else:
        form = DirectorForm()
    return render(request, "recommender/directors/director_admin_form.html", {"form": form})

def director_admin_detail(request, pk):
    director = get_object_or_404(Director, pk=pk)
    if request.method == "POST":
        form = DirectorForm(request.POST, instance=director)
        if form.is_valid():
            form.save()
            return redirect('director_admin_list')
    else:
        form = DirectorForm(instance=director)
    return render(request, "recommender/directors/director_admin_detail.html", {
        "director": director,
        "form": form
    })

def director_admin_update(request, pk):
    director = get_object_or_404(Director, pk=pk)
    if request.method == "POST":
        form = DirectorForm(request.POST, request.FILES, instance=director)
        if form.is_valid():
            form.save()
            return redirect("director_admin_list")
    else:
        form = DirectorForm(instance=director)
    return render(request, "recommender/directors/director_admin_form.html", {"form": form})

def director_admin_delete(request, pk):
    director = get_object_or_404(Director, pk=pk)
    if request.method == "POST":
        director.delete()
        return redirect("director_admin_list")
    return render(request, "recommender/directors/director_admin_confirm_delete.html", {"director": director})