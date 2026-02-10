from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "status",
            "created_at",
            "updated_at",
            "problem_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "problem_count"]

    problem_count = serializers.IntegerField(read_only=True)
