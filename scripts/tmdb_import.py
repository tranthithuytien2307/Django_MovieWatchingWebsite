import os
import django
import requests
import sys

# Thêm root project vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")

import django
django.setup()

from recommendations.models import Movie, Genre, Country, Director, Actor, Episode

TMDB_API_KEY = "85358aeaa358ce4d52fcded62b69891a"
BASE_URL = "https://api.themoviedb.org/3"

# ========================
# Helper: gọi TMDb API
# ========================
def fetch_movie_info(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "videos,credits"}
    return requests.get(url, params=params).json()

def fetch_tv_info(tv_id):
    url = f"{BASE_URL}/tv/{tv_id}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "videos,credits"}
    return requests.get(url, params=params).json()

def fetch_season_info(tv_id, season_number):
    url = f"{BASE_URL}/tv/{tv_id}/season/{season_number}"
    params = {"api_key": TMDB_API_KEY, "append_to_response": "videos"}
    return requests.get(url, params=params).json()

# ========================
# Insert Movie
# ========================
def insert_movie(movie):
    trailer_link = None
    for v in movie.get("videos", {}).get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer_link = f"https://www.youtube.com/watch?v={v['key']}"
            break

    genres = []
    for g in movie.get("genres", []):
        genre_obj, _ = Genre.objects.get_or_create(name=g["name"])
        genres.append(genre_obj)

    country_obj = None
    if movie.get("production_countries"):
        c = movie["production_countries"][0]
        country_obj, _ = Country.objects.get_or_create(name=c["name"])

    director_obj = None
    for crew in movie.get("credits", {}).get("crew", []):
        if crew["job"] == "Director":
            director_obj, _ = Director.objects.get_or_create(name=crew["name"])
            break

    actor_objs = []
    for cast in movie.get("credits", {}).get("cast", [])[:10]:
        actor_obj, _ = Actor.objects.get_or_create(name=cast["name"])
        actor_objs.append(actor_obj)

    movie_obj, created = Movie.objects.get_or_create(
        name=movie.get("title"),
        defaults={
            "movie_type": "movie",
            "release_year": int(movie.get("release_date", "2000")[:4]) if movie.get("release_date") else 2000,
            "country": country_obj,
            "director": director_obj,
            "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else "",
            "rating": float(movie.get("vote_average", 0.0)),
            "description": movie.get("overview", ""),
            "trailer_link": trailer_link,
        }
    )

    movie_obj.genres.set(genres)
    movie_obj.actors.set(actor_objs)

    print(f"✅ Đã insert movie: {movie_obj.name}")

# ========================
# Insert TV
# ========================
def insert_tv(tv):
    trailer_link = None
    for v in tv.get("videos", {}).get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            trailer_link = f"https://www.youtube.com/watch?v={v['key']}"
            break

    genres = []
    for g in tv.get("genres", []):
        genre_obj, _ = Genre.objects.get_or_create(name=g["name"])
        genres.append(genre_obj)

    country_obj = None
    if tv.get("production_countries"):
        c = tv["production_countries"][0]
        country_obj, _ = Country.objects.get_or_create(name=c["name"])

    director_obj = None
    for crew in tv.get("credits", {}).get("crew", []):
        if crew["job"] == "Director":
            director_obj, _ = Director.objects.get_or_create(name=crew["name"])
            break

    actor_objs = []
    for cast in tv.get("credits", {}).get("cast", [])[:10]:
        actor_obj, _ = Actor.objects.get_or_create(name=cast["name"])
        actor_objs.append(actor_obj)

    tv_obj, created = Movie.objects.get_or_create(
        name=tv.get("name"),
        defaults={
            "movie_type": "tv",
            "release_year": int(tv.get("first_air_date", "2000")[:4]) if tv.get("first_air_date") else 2000,
            "country": country_obj,
            "director": director_obj,
            "poster": f"https://image.tmdb.org/t/p/w500{tv['poster_path']}" if tv.get("poster_path") else "",
            "rating": float(tv.get("vote_average", 0.0)),
            "description": tv.get("overview", ""),
            "trailer_link": trailer_link,
        }
    )

    tv_obj.genres.set(genres)
    tv_obj.actors.set(actor_objs)

    print(f"✅ Đã insert TV series: {tv_obj.name}")

    # Chỉ lấy season 1, bỏ season 0 (specials)
    for season in tv.get("seasons", []):
        if season["season_number"] == 0:
            continue
        if season["season_number"] > 1:
            break
        season_info = fetch_season_info(tv["id"], season["season_number"])
        for ep in season_info.get("episodes", []):
            Episode.objects.get_or_create(
                movie=tv_obj,
                name=ep.get("name"),
                defaults={
                    "link": "",
                    "duration": ep.get("runtime") or 0,
                }
            )
            print(f"   📺 Inserted Episode {season['season_number']}x{ep['episode_number']}: {ep.get('name')}")

# ========================
# Chạy thử với nhiều phim/series
# ========================
if __name__ == "__main__":
    # 30 movies (ví dụ, bạn thay ID khác tùy thích)
    movie_ids = [
        # --- Mỹ (10) ---
        550,      # Fight Club
        603,      # The Matrix
        155,      # The Dark Knight
        278,      # The Shawshank Redemption
        680,      # Pulp Fiction
        13,       # Forrest Gump
        27205,    # Inception
        1891,     # The Empire Strikes Back
        122,      # The Lord of the Rings: The Return of the King
        238,      # The Godfather

        # --- Hàn Quốc (10) ---
        496243,   # Parasite (Ký Sinh Trùng)
        396535,   # Train to Busan (Chuyến Tàu Sinh Tử)
        670,      # Oldboy (2003)
        290859,   # The Handmaiden (Người Hầu Gái)
        447365,   # Along with the Gods: The Two Worlds (Thử Thách Thần Chết 1)
        438799,   # Along with the Gods: The Last 49 Days (Thử Thách Thần Chết 2)
        714888,   # Space Sweepers (Con Tàu Chiến Thắng)
        581528,   # Peninsula (Bán Đảo - Train to Busan 2)
        726429,   # Decision to Leave (Quyết Tâm Chia Tay)
        290098,   # The Wailing (Tiếng Than)

        # --- Trung Quốc (10) ---
        18823,    # Hero (Anh Hùng - 2002, Trương Nghệ Mưu)
        210577,   # The Great Wall (Vạn Lý Trường Thành)
        47971,    # The Grandmaster (Nhất Đại Tông Sư)
        10216,    # Ip Man (Diệp Vấn 1)
        228150,   # Ip Man 3
        449176,   # Wolf Warrior 2 (Chiến Lang 2)
        604605,   # The Wandering Earth (Lưu Lạc Địa Cầu 1)
        597208,   # The Wandering Earth 2 (Lưu Lạc Địa Cầu 2)
        77016,    # Painted Skin: The Resurrection (Họa Bì 2)
        58233     # Let the Bullets Fly (Nhượng Đạn Phi - 2010)
    ]

    for mid in movie_ids:
        movie = fetch_movie_info(mid)
        insert_movie(movie)

    # 10 TV series (chỉ lấy season 1)
    tv_ids = [
        66732,    # Stranger Things (Mỹ, Sci-Fi/Fantasy, Horror)
        37854,    # Sherlock (Anh, Crime, Drama, Mystery)
        1402,     # The Walking Dead (Mỹ, Action, Drama, Horror)
        60574,    # Peaky Blinders (Anh, Crime, Drama, History)
        1399,     # Game of Thrones (Mỹ, Fantasy, Adventure)
        66017,    # Dark (Đức, Sci-Fi, Mystery, Thriller)
        66788,    # Money Heist / La Casa de Papel (Tây Ban Nha, Crime, Thriller)
        82856,    # The Mandalorian (Mỹ, Action, Adventure, Sci-Fi)
        93405,    # Squid Game (Hàn Quốc, Drama, Thriller)
        124271    # The Longest Day In Chang'an (Trường An 12 Canh Giờ - Trung Quốc, Historical, Thriller)
    ]

    for tid in tv_ids:
        tv = fetch_tv_info(tid)
        insert_tv(tv)
