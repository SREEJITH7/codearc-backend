from rest_framework import serializers
from apps.auth_app.models import UserProfile


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "display_name",
            "bio",
            "skills",
            "profileImage",
            "linkedin",
            "github",
            "resume",
        ]
        extra_kwargs = {
            "profileImage": {"required": False},
            "resume": {"required": False},
        }

    # -----------------------------
    # 1️⃣ CLEAN EMPTY VALUES
    # -----------------------------
    def validate(self, attrs):
        cleaned = {}
        for key, value in attrs.items():
            if value not in ("", None):
                cleaned[key] = value
        return cleaned

    # -----------------------------
    # 2️⃣ VALIDATE SKILLS
    # -----------------------------
    def validate_skills(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills must be a list")

        for skill in value:
            if not isinstance(skill, str):
                raise serializers.ValidationError("Each skill must be a string")

        return value

    # -----------------------------
    # 3️⃣ VALIDATE RESUME FILE
    # -----------------------------
    def validate_resume(self, file):
        if file.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume must be under 5MB")

        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        if file.content_type not in allowed_types:
            raise serializers.ValidationError("Invalid resume file type")

        return file

    # -----------------------------
    # 4️⃣ DELETE OLD RESUME ON UPDATE
    # -----------------------------
    def update(self, instance, validated_data):
        new_resume = validated_data.get("resume")

        if new_resume and instance.resume:
            instance.resume.delete(save=False)

        return super().update(instance, validated_data)
