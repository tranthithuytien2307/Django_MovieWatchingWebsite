from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Director, Episode, Country
from .forms import MovieForm
from .models import AppUser, Genre, Actor, Country, Review
from .forms import DirectorForm
from .forms import ActorForm
from urllib.parse import urlparse, parse_qs
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import calendar
from django.shortcuts import render
from .models import Movie

def admin_dashboard(request):
    # Top 5 phim có lượt xem nhiều nhất
    top_movies = Movie.objects.order_by('-views')[:5]

    labels = [movie.name for movie in top_movies]
    views = [movie.views for movie in top_movies]

    # Các thống kê cơ bản
    stats = {
        'movies': Movie.objects.count(),
        'users': {'total': AppUser.objects.count()},
        'actors': Actor.objects.count(),
        'directors': Director.objects.count(),
        'genres': Genre.objects.count(),
        'countries': Country.objects.count(),
        'reviews': Review.objects.count(), 
    }

    # Tạo list card để loop trong template
    cards = [
        {'value': stats['movies'], 'icon': 'fa-film', 'label': 'Tổng số phim', 'bg': 'linear-gradient(135deg,#3498db,#2980b9)', 'url': 'movie_admin_list'},
        {'value': stats['users']['total'], 'icon': 'fa-users', 'label': 'Người dùng', 'bg': 'linear-gradient(135deg,#8e44ad,#71368a)', 'url': 'users_list'},
        {'value': stats['actors'], 'icon': 'fa-person', 'label': 'Diễn viên', 'bg': 'linear-gradient(135deg,#27ae60,#1e8449)', 'url': 'actor_list'},
        {'value': stats['directors'], 'icon': 'fa-video', 'label': 'Đạo diễn', 'bg': 'linear-gradient(135deg,#c0392b,#992d22)', 'url': 'director_admin_list'},
        {'value': stats.get('genres', 0), 'icon': 'fa-tags', 'label': 'Thể loại', 'bg': 'linear-gradient(135deg,#f39c12,#d68910)', 'url': 'genre_country_admin'},
        {'value': stats.get('countries', 0), 'icon': 'fa-globe', 'label': 'Quốc gia', 'bg': 'linear-gradient(135deg,#16a085,#138d75)', 'url': 'genre_country_admin'},
        {'value': stats['reviews'], 'icon': 'fa-comments', 'label': 'Review', 'bg': 'linear-gradient(135deg,#e67e22,#d35400)', 'url': 'review_admin_list'},
    ]

    context = {
        'stats': stats,
        'labels': labels,
        'views': views,
        'cards': cards,
    }

    return render(request, 'recommender/admin_dashboard.html', context)

# Trang user
def users_list(request):
    users = AppUser.objects.all()
    return render(request, "recommender/admin/users_list.html", {"users": users})

def user_detail(request, pk):
    user = get_object_or_404(AppUser, pk=pk)
    return render(request, "recommender/admin/user_detail.html", {"user": user})
def user_edit(request, pk):
    user = get_object_or_404(AppUser, pk=pk)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")
        avatar = request.POST.get("avatar")

        # Kiểm tra email trùng (ngoại trừ chính user này)
        if AppUser.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "Email đã tồn tại!")
            return redirect("user_edit", pk=pk)

        # Kiểm tra phone trùng
        if AppUser.objects.exclude(pk=user.pk).filter(phone=phone).exists():
            messages.error(request, "Số điện thoại đã tồn tại!")
            return redirect("user_edit", pk=pk)

        # Cập nhật dữ liệu
        user.name = name
        user.email = email
        user.phone = phone
        user.role = role
        user.avatar = avatar
        user.save()

        messages.success(request, "Cập nhật user thành công!")
        return redirect("user_detail", pk=pk)

    return render(request, "recommender/admin/user_edit.html", {"user": user})

def user_change_password(request, pk):
    user = get_object_or_404(AppUser, pk=pk)

    if request.method == "POST":
        step = request.POST.get("step")

        # ----- BƯỚC 1: XÁC MINH MẬT KHẨU HIỆN TẠI -----
        if step == "verify":
            current_password = request.POST.get("current_password")

            if not user.check_password(current_password):
                messages.error(request, "Mật khẩu hiện tại không đúng!")
                return redirect("user_change_password", pk=pk)

            # Nếu đúng → render sang form nhập mật khẩu mới
            return render(request, "recommender/admin/user_change_password_step2.html", {"user": user})

        # ----- BƯỚC 2: ĐỔI MẬT KHẨU -----
        elif step == "change":
            password = request.POST.get("password")
            confirm = request.POST.get("confirm")

            if password != confirm:
                messages.error(request, "Mật khẩu xác nhận không khớp!")
                return redirect("user_change_password", pk=pk)

            if len(password) < 6:
                messages.error(request, "Mật khẩu phải ít nhất 6 ký tự!")
                return redirect("user_change_password", pk=pk)

            user.set_password(password)
            user.save()

            messages.success(request, "Đổi mật khẩu thành công!")
            return redirect("user_detail", pk=pk)

    # MẶC ĐỊNH HIỂN THỊ BƯỚC 1
    return render(request, "recommender/admin/user_change_password.html", {"user": user})

def user_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        role = request.POST.get("role")

        AppUser.objects.create(
            name=name,
            email=email,
            phone=phone,
            role=role,
            status=True
        )

        messages.success(request, "Tạo user thành công!")
        return redirect("users_list")

    return render(request, "recommender/admin/user_create.html")


def user_toggle_status(request, pk):
    user = get_object_or_404(AppUser, pk=pk)
    user.status = not user.status
    user.save()
    return redirect("user_detail", pk=pk)


def movie_admin_list(request):
    search_query = request.GET.get('search', '').strip()  # Lấy query search

    # Lọc movie theo search (tên phim)
    if search_query:
        movie_list = Movie.objects.filter(
            Q(name__icontains=search_query)
        ).order_by('-id')
    else:
        movie_list = Movie.objects.all().order_by('-id')

    # Phân trang: 12 phim / trang
    paginator = Paginator(movie_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,  # để giữ value search trên input
    }
    return render(request, "recommender/movie_admin_list.html", context)


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
    search_query = request.GET.get("search", "")

    directors_list = Director.objects.all().order_by("name")

    # Search
    if search_query:
        directors_list = directors_list.filter(name__icontains=search_query)

    # Pagination
    paginator = Paginator(directors_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "recommender/directors/director_admin_list.html", {
        "page_obj": page_obj,
        "search_query": search_query,
    })


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

def actor_list(request):
    query = request.GET.get("search", "")
    actors = Actor.objects.all().order_by("name")

    if query:
        actors = actors.filter(
            Q(name__icontains=query)
        )

    paginator = Paginator(actors, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "recommender/actors/actor_list.html", {
        "page_obj": page_obj,
        "query": query
    })

def actor_detail(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    movies = actor.movies.all()    # ManyToMany → danh sách phim tham gia

    return render(request, "recommender/actors/actor_detail.html", {
        "actor": actor,
        "movies": movies
    })
def actor_create(request):
    if request.method == "POST":
        form = ActorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã thêm diễn viên thành công!")
            return redirect("actor_list")
    else:
        form = ActorForm()

    return render(request, "recommender/actors/actor_form.html", {
        "form": form,
        "title": "Thêm diễn viên"
    })

# -----------------------------------
# Edit
# -----------------------------------
def actor_edit(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    if request.method == "POST":
        form = ActorForm(request.POST, instance=actor)
        if form.is_valid():
            form.save()
            messages.success(request, "Cập nhật diễn viên thành công!")
            return redirect("actor_detail", actor_id=actor.id)
    else:
        form = ActorForm(instance=actor)

    return render(request, "recommender/actors/actor_form.html", {
        "form": form,
        "title": "Chỉnh sửa diễn viên"
    })

# -----------------------------------
# Delete
# -----------------------------------
def actor_delete(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)

    if request.method == "POST":
        actor.delete()
        messages.success(request, "Đã xóa diễn viên!")
        return redirect("actor_list")

    return render(request, "recommender/actors/actor_delete_confirm.html", {
        "actor": actor
    })


def genre_country_admin(request):
    genres = Genre.objects.all().order_by("name")
    countries = Country.objects.all().order_by("name")

    return render(request, "recommender/admin/genre_country.html", {
        "genres": genres,
        "countries": countries
    })
def genre_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        Genre.objects.create(name=name)
    return redirect("genre_country_admin")
def country_add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        code = request.POST.get("code")
        Country.objects.create(name=name, code=code)
    return redirect("genre_country_admin")
def genre_delete(request, id):
    genre = get_object_or_404(Genre, id=id)
    genre.delete()
    return redirect("genre_country_admin")

def country_delete(request, id):
    country = get_object_or_404(Country, id=id)
    country.delete()
    return redirect("genre_country_admin")
def genre_edit(request, id):
    genre = get_object_or_404(Genre, id=id)
    if request.method == "POST":
        genre.name = request.POST.get("name")
        genre.save()
        return redirect("genre_country_admin")
    return render(request, "recommender/admin/genre_edit.html", {"genre": genre})

def country_edit(request, id):
    country = get_object_or_404(Country, id=id)
    if request.method == "POST":
        country.name = request.POST.get("name")
        country.code = request.POST.get("code")
        country.save()
        return redirect("genre_country_admin")
    return render(request, "recommender/admin/country_edit.html", {"country": country})


def review_admin_list(request):
    query = request.GET.get('search', '')  # Lấy từ khóa search từ input
    movies = Movie.objects.prefetch_related('reviews').all()
    
    if query:
        movies = movies.filter(name__icontains=query)  # Lọc phim theo tên

    context = {
        'movies_with_reviews': movies,
        'query': query,
    }
    return render(request, 'recommender/review/admin_review_list.html', context)

def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('review_admin_list')