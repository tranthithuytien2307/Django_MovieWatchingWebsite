import os
import sys
import django

# 🔧 Thiết lập đường dẫn và cấu hình Django (giống các script khác)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")

django.setup()

from recommendations.models import Country


def fix_country_codes():
    used_codes = set(
        Country.objects.exclude(code__isnull=True).values_list("code", flat=True)
    )

    for country in Country.objects.filter(code__isnull=True):
        base_code = country.name[:2].upper()

        # 🔁 Tạo mã không trùng
        code = base_code
        counter = 1
        while code in used_codes or Country.objects.filter(code=code).exists():
            counter += 1
            code = f"{base_code}{counter}"

        country.code = code
        country.save()
        used_codes.add(code)

        print(f"✅ {country.name} -> {country.code}")

    print("🎯 Hoàn tất cập nhật code cho tất cả quốc gia thiếu mã.")


if __name__ == "__main__":
    fix_country_codes()
