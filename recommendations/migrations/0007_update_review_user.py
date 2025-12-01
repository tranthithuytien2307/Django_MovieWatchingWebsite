# Generated manually to fix Review user migration
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

def copy_reviewer_to_user(apps, schema_editor):
    Review = apps.get_model("recommendations", "Review")
    for review in Review.objects.all():
        if hasattr(review, "reviewer") and review.reviewer:
            review.user_id = review.reviewer_id
            review.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recommendations', '0006_genre_slug'),
    ]

    operations = [
        # 1. Thêm field user trước
        migrations.AddField(
            model_name='review',
            name='user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reviews',
                null=True,  # null=True tạm thời để tránh lỗi migration
                blank=True,
            ),
        ),
        # 2. Copy dữ liệu từ reviewer sang user
        migrations.RunPython(copy_reviewer_to_user, reverse_code=migrations.RunPython.noop),
        # 3. Xóa field reviewer
        migrations.RemoveField(
            model_name='review',
            name='reviewer',
        ),
        # 4. Đặt unique_together
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('movie', 'user')},
        ),
    ]
