from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source="user.name")  # tên user tự động

    class Meta:
        model = Review
        fields = ["id", "movie", "reviewer", "rating", "content", "created_at"]
        read_only_fields = ["id", "reviewer", "created_at"]

    def validate_rating(self, rating):
        if rating < 1 or rating > 5:
            raise serializers.ValidationError("Điểm đánh giá phải từ 1 đến 5")
        return rating
