

from rest_framework import serializers
from .models import Problem, TestCases , Category

# In your serializers.py
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestCasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCases
        fields = ["id", "input", "expected_output", "is_sample","order",]

class ProblemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True
    )
    testcases = TestCasesSerializer(many=True, read_only=True)

    status = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = [
            "id",
            "title",
            "description",
            "difficulty",
            "category",
            "category_id",
            "tags",
            "examples",
            "hints",
            "function_name",
            "parameters",
            "return_type",
            "constraints",
            "starter_code",
            "supported_languages",
            "solution",
            "time_limit",
            "memory_limit",
            "is_premium",
            "visible",
            "status",
            "testcases",
            "created_at",
        ]

    def create(self, validated_data):
        testcases_data = self.initial_data.get('testcases', [])
        problem = Problem.objects.create(**validated_data)
        
        for tc in testcases_data:
            TestCases.objects.create(problem=problem, **tc)
            
        return problem

    def get_status(self, obj):
        return "Active" if obj.is_active else "InActive"

