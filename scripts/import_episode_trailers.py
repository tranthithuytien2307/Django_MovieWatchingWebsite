import os
import django
import sys
import requests

# trỏ về thư mục gốc của project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# chỉ định settings chính xác
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")

django.setup()

from recommendations.models import Movie, Episode

TMDB_API_KEY = "85358aeaa358ce4d52fcded62b69891a"  # thay bằng API key thật

def import_episode_trailers(movie):
    if not movie.tmdb_id:
        print(f"❌ {movie.name} chưa có tmdb_id")
        return

    # gọi API để lấy danh sách season của TV show
    url = f"https://api.themoviedb.org/3/tv/{movie.tmdb_id}?api_key={TMDB_API_KEY}&language=vi-VN"
    resp = requests.get(url).json()

    for season in resp.get("seasons", []):
        season_number = season["season_number"]
        print(f"\n📺 {movie.name} - Season {season_number}")

        # gọi API để lấy danh sách tập
        ep_url = f"https://api.themoviedb.org/3/tv/{movie.tmdb_id}/season/{season_number}?api_key={TMDB_API_KEY}&language=vi-VN"
        episodes = requests.get(ep_url).json().get("episodes", [])

        for ep in episodes:
            ep_number = ep["episode_number"]
            ep_name = ep.get("name") or f"Tập {ep_number}"

            # gọi API để lấy video trailer của từng tập
            video_url = f"https://api.themoviedb.org/3/tv/{movie.tmdb_id}/season/{season_number}/episode/{ep_number}/videos?api_key={TMDB_API_KEY}&language=vi-VN"
            videos = requests.get(video_url).json().get("results", [])

            trailer_link = ""
            for v in videos:
                if v["site"] == "YouTube" and v["type"] in ["Trailer", "Teaser", "Clip"]:
                    trailer_link = f"https://www.youtube.com/embed/{v['key']}"
                    break

            if not trailer_link:
                print(f"⚠️ {movie.name} S{season_number}E{ep_number} chưa có trailer")
                continue

            # cập nhật hoặc tạo mới Episode
            episode_obj, created = Episode.objects.get_or_create(
                movie=movie,
                season_number=season_number,
                episode_number=ep_number,
                defaults={
                    "name": ep_name,
                    "duration": ep.get("runtime") or 60,
                    "link": trailer_link,
                }
            )

            if not created:
                episode_obj.name = ep_name
                episode_obj.link = trailer_link
                episode_obj.duration = ep.get("runtime") or episode_obj.duration
                episode_obj.save()

            print(f"✅ {movie.name} - {ep_name} → {trailer_link}")


if __name__ == "__main__":
    movies = Movie.objects.filter(tmdb_id__isnull=False)
    print(f"🔍 Tìm thấy {movies.count()} phim có tmdb_id, bắt đầu import...\n")

    for movie in movies:
        try:
            import_episode_trailers(movie)
        except Exception as e:
            print(f"💥 Lỗi khi xử lý {movie.name}: {e}")

    print("\n🎉 Import trailers hoàn tất!")
