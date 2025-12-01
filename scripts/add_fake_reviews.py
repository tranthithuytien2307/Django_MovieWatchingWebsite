import os
import sys
import django
import random
from faker import Faker  # pip install faker nếu chưa có

# ================== setup Django ==================
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_site.settings")
django.setup()

from recommendations.models import Movie, AppUser, Review

fake = Faker()

NUM_REVIEWS_PER_MOVIE = 5  # số review mỗi phim

def create_fake_reviews():
    movies = Movie.objects.all()
    users = list(AppUser.objects.all())
    if not users:
        print("⚠️ Chưa có user nào trong DB, hãy tạo user trước.")
        return

    for movie in movies:
        for _ in range(NUM_REVIEWS_PER_MOVIE):
            user = random.choice(users)
            # tránh duplicate (movie, user)
            if Review.objects.filter(movie=movie, user=user).exists():
                continue

            rating = random.randint(1, 5)
            content = fake.paragraph(nb_sentences=3)

            review = Review.objects.create(
                movie=movie,
                user=user,
                rating=rating,
                content=content
            )
            print(f"✅ Thêm review: {user.email} - {movie.name} ({rating}⭐)")

if __name__ == "__main__":
    create_fake_reviews()
    print("🎉 Hoàn tất thêm dữ liệu review giả.")
