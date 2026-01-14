

import json
from rest_framework import serializers
from .models import Problem, TestCases , Category , Submission

# In your serializers.py
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestCasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCases
        fields = ["id", "input", "expected_output", "is_sample", "order"]

    def _try_parse_json(self, value):
        if not isinstance(value, str):
            return value
        
        trimmed = value.strip()
        if not trimmed:
            return value
            
        try:
            # Try to parse as JSON (handles numbers, lists, objects, bools, strings with quotes)
            return json.loads(trimmed)
        except (json.JSONDecodeError, ValueError):
            return value

    def validate_input(self, value):
        # Value should be a list of inputs. Each element might need parsing.
        if not isinstance(value, list):
            raise serializers.ValidationError("Input must be a list of values.")
            
        parsed_inputs = []
        for val in value:
            parsed_inputs.append(self._try_parse_json(val))
        return parsed_inputs

    def validate_expected_output(self, value):
        return self._try_parse_json(value)

class ProblemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True
    )
    testcases = TestCasesSerializer(many=True, required=False)

    is_solved = serializers.SerializerMethodField()
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
            "is_solved",
            "testcases",
            "created_at",
        ]

    def create(self, validated_data):
        testcases_data = validated_data.pop('testcases', [])
        problem = Problem.objects.create(**validated_data)
        
        for tc_data in testcases_data:
            TestCases.objects.create(problem=problem, **tc_data)
            
        return problem

    def validate(self, data):
        parameters = data.get('parameters', self.instance.parameters if self.instance else [])
        testcases = data.get('testcases')

        if testcases is not None:
            num_params = len(parameters)
            param_types = [p.get('type', '').lower() for p in parameters]

            for i, tc in enumerate(testcases):
                tc_input = tc.get('input', [])
                
                # Check length match
                if len(tc_input) != num_params:
                    raise serializers.ValidationError(
                        f"TestCase {i+1}: Input count ({len(tc_input)}) must match parameter count ({num_params})"
                    )

                # Check type nesting
                for idx, (val, p_type) in enumerate(zip(tc_input, param_types)):
                    is_array_type = '[]' in p_type or 'list' in p_type or 'array' in p_type
                    
                    if isinstance(val, list) and not is_array_type:
                        # If it's a list but the type is int/string/bool/float, it's likely double-nested [[val]]
                        # unless it's genuinely a nested list (which we can check by looking if it's a list of length 1)
                        # but usually, users just shouldn't wrap scalars in brackets.
                        raise serializers.ValidationError(
                            f"TestCase {i+1}, Arg {idx+1}: Parameter '{parameters[idx]['name']}' is '{p_type}', but you provided a list: {val}. Please remove brackets if it's a single value."
                        )

        return data

    def update(self, instance, validated_data):
        testcases_data = validated_data.pop('testcases', None)
        
        # Update problem fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Atomic replacement for test cases if provided
        if testcases_data is not None:
            instance.testcases.all().delete()
            for tc_data in testcases_data:
                TestCases.objects.create(problem=instance, **tc_data)
        
        return instance

    def get_is_solved(self, obj):
        solved_ids = self.context.get('solved_problem_ids', set())
        return obj.id in solved_ids

    def get_status(self, obj):
        return "Active" if obj.is_active else "InActive"

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"
        read_only_fields = ["user", "status", "passed_count", "total_count", "created_at"]

        