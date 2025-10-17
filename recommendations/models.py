import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# ========================
# Quản lý user
# ========================
class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Người dùng phải có email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # dùng hàm có sẵn
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ========================
# Người dùng
# ========================
class AppUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.CharField(max_length=50, default="customer")  # admin, customer,...
    status = models.BooleanField(default=True)  # active/inactive

    # Trường cần thiết cho Django auth
    is_staff = models.BooleanField(default=False)  # cho phép vào Django admin
    is_active = models.BooleanField(default=True)  # user còn hoạt động

    objects = AppUserManager()

    USERNAME_FIELD = "email"  # login bằng email
    REQUIRED_FIELDS = ["name", "phone"]

    def __str__(self):
        return self.email

# ========================
# Token lưu access/refresh
# ========================
class UserToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="tokens")
    access_token = models.CharField(max_length=512, null=True, blank=True)
    refresh_token = models.CharField(max_length=512, null=True, blank=True)
    access_expires_at = models.DateTimeField(null=True, blank=True)
    refresh_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user.email}"


# ========================
# Thể loại phim
# ========================
class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ========================
# Quốc gia
# ========================
class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ========================
# Đạo diễn
# ========================
class Director(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    avatar = models.URLField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# ========================
# Diễn viên
# ========================
class Actor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    avatar = models.URLField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True, null=True) 

    def __str__(self):
        return self.name


# ========================
# Thông tin phim
# ========================
class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    movie_type = models.CharField(max_length=50)  # phim lẻ / phim bộ
    release_year = models.IntegerField()
    genres = models.ManyToManyField(Genre, related_name="movies")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name="movies")
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, related_name="movies")
    actors = models.ManyToManyField(Actor, related_name="movies")
    views = models.IntegerField(default=0)
    poster = models.URLField(blank=True)
    rating = models.FloatField(default=0.0)
    status = models.BooleanField(default=True)  # còn chiếu / ngừng chiếu
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    trailer_link = models.URLField(blank=True, null=True)  # thêm mới
    def save(self, *args, **kwargs):
        if self.trailer_link and "watch?v=" in self.trailer_link:
            self.trailer_link = self.trailer_link.replace("watch?v=", "embed/")
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


# ========================
# Danh sách tập phim
# ========================
class Episode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="episodes")
    name = models.CharField(max_length=200)  # tên tập phim
    link = models.URLField(help_text="Link trailer của tập")  # dùng luôn cho trailer
    duration = models.IntegerField(help_text="Thời lượng (phút)")
    status = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if self.link and "watch?v=" in self.link:
            self.link = self.link.replace("watch?v=", "embed/")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movie.name} - {self.name}"


# ========================
# Review phim
# ========================
class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.CharField(max_length=100)  # tên người review
    rating = models.IntegerField()  # điểm đánh giá
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer} - {self.movie.name}"


# ========================
# Đơn hàng
# ========================
class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)  # tên đơn
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)  # pending, completed, cancelled
    payment_method = models.CharField(max_length=50)  # cash, paypal, momo,...
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="orders")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
