import os
import sys
import django

# thêm đường dẫn cha của 'scripts' (tức là thư mục gốc movie_recommender)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")
django.setup()

from recommendations.models import Movie   # import model


# ========================
# ID phim lẻ (movie_ids)
# ========================
movie_ids = {
    550: "Fight Club",
    603: "The Matrix",
    155: "The Dark Knight",
    278: "The Shawshank Redemption",
    680: "Pulp Fiction",
    13: "Forrest Gump",
    27205: "Inception",
    1891: "The Empire Strikes Back",
    122: "The Lord of the Rings: The Return of the King",
    238: "The Godfather",

    496243: "Parasite",
    396535: "Train to Busan",
    670: "Oldboy",
    290859: "The Handmaiden",
    447365: "Along with the Gods: The Two Worlds",
    438799: "Along with the Gods: The Last 49 Days",
    714888: "Space Sweepers",
    581528: "Peninsula",
    726429: "Decision to Leave",
    290098: "The Wailing",

    18823: "Hero",
    210577: "The Great Wall",
    47971: "The Grandmaster",
    10216: "Ip Man",
    228150: "Ip Man 3",
    449176: "Wolf Warrior 2",
    604605: "The Wandering Earth",
    597208: "The Wandering Earth 2",
    77016: "Painted Skin: The Resurrection",
    58233: "Let the Bullets Fly",
}

# ========================
# ID TV series (tv_ids)
# ========================
tv_ids = {
    66732: "Stranger Things",
    37854: "Sherlock",
    1402: "The Walking Dead",
    60574: "Peaky Blinders",
    1399: "Game of Thrones",
    66017: "Dark",
    66788: "Money Heist",
    82856: "The Mandalorian",
    93405: "Squid Game",
    124271: "The Longest Day In Chang'an",
}

def update_tmdb_ids(mapping, is_tv=False):
    for tmdb_id, title in mapping.items():
        try:
            movie = Movie.objects.get(name=title)
            if not hasattr(movie, "tmdb_id"):
                print(f"⚠️ Bỏ qua {title} vì model chưa có field tmdb_id")
                continue

            if movie.tmdb_id:  # đã có rồi thì không cần update
                print(f"ℹ️ {title} đã có tmdb_id={movie.tmdb_id}, bỏ qua")
                continue

            movie.tmdb_id = tmdb_id
            # nếu muốn phân biệt phim lẻ / series thì update luôn movie_type
            movie.movie_type = "tv" if is_tv else "movie"
            movie.save()
            print(f"✔ Updated {title} với tmdb_id={tmdb_id}")
        except Movie.DoesNotExist:
            print(f"❌ {title} không có trong DB")

if __name__ == "__main__":
    update_tmdb_ids(movie_ids, is_tv=False)
    update_tmdb_ids(tv_ids, is_tv=True)
    print("🎉 Hoàn tất update tmdb_id cho phim trong DB")
