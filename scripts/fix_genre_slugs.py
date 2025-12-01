import os
import sys
import django
from django.utils.text import slugify

# 🔧 Thiết lập đường dẫn và cấu hình Django (giống các script khác)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")

django.setup()

from recommendations.models import Genre


def fix_genre_slugs():
    updated = 0
    for genre in Genre.objects.all():
        if not genre.slug:
            genre.slug = slugify(genre.name)
            genre.save()
            print(f"✅ {genre.name} -> {genre.slug}")
            updated += 1

    if updated == 0:
        print("🎯 Tất cả thể loại đã có slug, không cần cập nhật.")
    else:
        print(f"🎬 Hoàn tất, đã cập nhật slug cho {updated} thể loại.")


if __name__ == "__main__":
    fix_genre_slugs()
