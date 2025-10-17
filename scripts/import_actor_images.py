import os
import sys
import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")

django.setup()

from recommendations.models import Movie, Actor

TMDB_API_KEY = "85358aeaa358ce4d52fcded62b69891a"
BASE_URL = "https://api.themoviedb.org/3"


def fetch_credits(movie_id, movie_type="movie"):
    url = f"{BASE_URL}/{movie_type}/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}
    return requests.get(url, params=params).json()


def update_actor_images_from_movies():
    movies = Movie.objects.all()
    for movie in movies:
        if not hasattr(movie, "tmdb_id") or not movie.tmdb_id:
            print(f"⚠️ Movie '{movie.name}' không có tmdb_id, bỏ qua.")
            continue

        credits = fetch_credits(movie.tmdb_id, movie.movie_type)
        for cast in credits.get("cast", [])[:10]:
            actor_name = cast["name"]
            profile_path = cast.get("profile_path")

            if not profile_path:
                continue

            try:
                actor = Actor.objects.get(name=actor_name)
                if not actor.image:  # chỉ update nếu chưa có
                    actor.image = f"https://image.tmdb.org/t/p/w500{profile_path}"
                    actor.save()
                    print(f"✅ Cập nhật ảnh cho: {actor.name} ({movie.name})")
            except Actor.DoesNotExist:
                print(f"⚠️ Không tìm thấy actor {actor_name} trong DB")


if __name__ == "__main__":
    update_actor_images_from_movies()
    print("🎉 Hoàn tất cập nhật ảnh diễn viên theo credits phim/series trong DB.")
