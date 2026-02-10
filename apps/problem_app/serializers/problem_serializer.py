from rest_framework import serializers
from ..models import Problem, TestCases, Category
from .category_serializer import CategorySerializer
from .testcase_serializer import TestCasesSerializer


class ProblemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )

    testcases = TestCasesSerializer(many=True, required=False)

    is_solved = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    acceptanceRate = serializers.SerializerMethodField()

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
            "is_solved",
            "acceptanceRate",
            "testcases",
            "created_at",
        ]


    def create(self, validated_data):
        testcases_data = validated_data.pop("testcases", [])
        problem = Problem.objects.create(**validated_data)

        for tc in testcases_data:
            TestCases.objects.create(problem=problem, **tc)

        return problem

    def update(self, instance, validated_data):
        testcases_data = validated_data.pop("testcases", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if testcases_data is not None:
            instance.testcases.all().delete()
            for tc in testcases_data:
                TestCases.objects.create(problem=instance, **tc)

        return instance


    def validate(self, data):
        parameters = data.get(
            "parameters",
            self.instance.parameters if self.instance else [],
        )
        testcases = data.get("testcases")

        if not testcases:
            return data

        num_params = len(parameters)
        param_types = [p.get("type", "").lower() for p in parameters]

        for i, tc in enumerate(testcases):
            tc_input = tc.get("input", [])

            if len(tc_input) != num_params:
                raise serializers.ValidationError(
                    f"TestCase {i+1}: Expected {num_params} inputs, got {len(tc_input)}"
                )

            for idx, (val, p_type) in enumerate(zip(tc_input, param_types)):
                is_array = any(x in p_type for x in ["[]", "list", "array"])
                if isinstance(val, list) and not is_array:
                    raise serializers.ValidationError(
                        f"TestCase {i+1}, Arg {idx+1}: "
                        f"'{parameters[idx]['name']}' expects {p_type}, got list {val}"
                    )

        return data

   

    def get_is_solved(self, obj):
        solved_ids = self.context.get("solved_problem_ids", set())
        return obj.id in solved_ids

    def get_status(self, obj):
        return "Active" if obj.is_active else "InActive"

    def get_acceptanceRate(self, obj):
        if obj.total_submissions == 0:
            return 0
        return round((obj.accepted_submissions / obj.total_submissions) * 100, 2)
