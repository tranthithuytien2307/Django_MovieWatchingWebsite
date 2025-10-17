import random
from datetime import date
from django.core.management.base import BaseCommand
from recommendations.models import (
    AppUser, UserToken, Genre, Country, Director,
    Actor, Movie, Episode, Review, Order
)


class Command(BaseCommand):
    help = "Seed database with sample data"

    def handle(self, *args, **kwargs):
        # ================= XÓA DỮ LIỆU CŨ =================
        self.stdout.write("🗑 Xóa dữ liệu cũ...")

        Order.objects.all().delete()
        Review.objects.all().delete()
        Episode.objects.all().delete()
        Movie.objects.all().delete()
        Actor.objects.all().delete()
        Director.objects.all().delete()
        Country.objects.all().delete()
        Genre.objects.all().delete()
        UserToken.objects.all().delete()
        AppUser.objects.all().delete()

        # ================= TẠO USERS =================
        self.stdout.write("👤 Tạo users...")

        # ================= TẠO USERS =================
        users = []

        # Admin (superuser)
        admin = AppUser.objects.create_superuser(
            name="Admin",
            email="admin@gmail.com",
            phone="0900000000",
            password="admin123"
        )
        users.append(admin)

        # Customers
        for i in range(1, 6):
            u = AppUser.objects.create_user(
                name=f"User {i}",
                email=f"user{i}@example.com",
                phone=f"0900{i}5678",
                password="123456",
                role="customer",
                status=True,
            )
            users.append(u)
            

        # ================= TẠO GENRES =================
        genres = [Genre.objects.create(name=n) for n in [
            "Hành động", "Hài hước", "Kinh dị", "Tình cảm",
            "Khoa học viễn tưởng", "Hoạt hình", "Phiêu lưu", "Tâm lý"
        ]]

        # ================= TẠO COUNTRIES =================
        countries = [Country.objects.create(name=n) for n in [
            "Mỹ", "Hàn Quốc", "Nhật Bản", "Việt Nam", "Pháp", "Ấn Độ"
        ]]

        # ================= TẠO DIRECTORS =================
        directors = []
        for i in range(1, 6):
            d = Director.objects.create(
                name=f"Director {i}",
                birthday=date(1970+i, 1, 1),
                description=f"Đạo diễn số {i}"
            )
            directors.append(d)

        # ================= TẠO ACTORS =================
        actors = []
        for i in range(1, 11):
            a = Actor.objects.create(
                name=f"Actor {i}",
                birthday=date(1980+i, 6, 15),
                description=f"Diễn viên số {i}"
            )
            actors.append(a)

        # ================= TẠO MOVIES =================
        movies = []
        for i in range(1, 6):
            m = Movie.objects.create(
                name=f"Movie {i}",
                movie_type="phim bộ" if i % 2 == 0 else "phim lẻ",
                release_year=2000+i,
                country=random.choice(countries),
                director=random.choice(directors),
                views=random.randint(100, 10000),
                rating=round(random.uniform(5, 9), 1),
                price=random.randint(50000, 150000),
                description=f"Mô tả cho phim {i}"
            )
            m.genres.set(random.sample(genres, k=2))
            m.actors.set(random.sample(actors, k=3))
            movies.append(m)

        # ================= TẠO EPISODES =================
        for m in movies:
            for j in range(1, 4):
                Episode.objects.create(
                    movie=m,
                    name=f"Tập {j}",
                    link=f"http://example.com/{m.id}/{j}",
                    duration=random.randint(20, 120)
                )

        # ================= TẠO REVIEWS =================
        for m in movies:
            for j in range(3):
                u = random.choice(users)
                Review.objects.create(
                    movie=m,
                    reviewer=u.name,  # ⚡ vì field reviewer là CharField
                    rating=random.randint(1, 10),
                    content=f"Nhận xét {j+1} cho {m.name}"
                )

        # ================= TẠO ORDERS =================
        for i in range(5):
            Order.objects.create(
                name=f"Order {i+1}",
                status=random.choice(["pending", "completed", "cancelled"]),
                payment_method=random.choice(["cash", "paypal", "momo"]),
                movie=random.choice(movies),
                price=random.randint(50000, 150000)
            )

        self.stdout.write(self.style.SUCCESS("✅ Seed data thành công!"))
