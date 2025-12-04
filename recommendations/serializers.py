from rest_framework import serializers
from .models import Movie, Review

class ReviewSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.name', read_only=True)
    userAvatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'movie', 'user', 'userName', 'userAvatar', 'rating', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'userName', 'userAvatar', 'created_at']

    def validate_rating(self, rating):
        if rating < 1 or rating > 5:
            raise serializers.ValidationError("Điểm đánh giá phải từ 1 đến 5")
        return rating
