import json
from rest_framework import serializers
from ..models import TestCases


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
            return json.loads(trimmed)
        except (json.JSONDecodeError, ValueError):
            return value

   

    def validate_input(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Input must be a list of values.")

        return [self._try_parse_json(v) for v in value]

    def validate_expected_output(self, value):
        return self._try_parse_json(value)
