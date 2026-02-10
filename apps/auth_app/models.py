# auth_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
import random
import string

ROLE_CHOICES = (
    ("user", "User"),
    ("recruiter", "Recruiter"),
    ("admin", "Admin"),
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class UserProfile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")    
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)  
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    profileImage = models.ImageField(upload_to="profile_image", blank= True , null = True)
    linkedin = models.URLField(blank=True, null= True)
    github = models.URLField(blank=True, null = True)
    total_submissions = models.PositiveIntegerField(default=0)
    problems_solved = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} profile"


class RecruiterProfile(models.Model):
    """
    Profile for recruiters. OneToOne with User.
    Contains company info and verification flags.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("Active", "Active"),
        ("reject", "Rejected"),
        ("InActive", "Inactive"),
    )
    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="recruiter_profile")
    company_name = models.CharField(max_length=255, blank=True)
    company_type = models.CharField(max_length=255, blank=True)
    year_established = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    registration_certificate = models.FileField(upload_to="recruiter_docs/", blank=True, null=True)
    is_company_verified = models.BooleanField(default=False)
    contact_person = models.CharField(max_length=150, blank=True)

    profileimage = models.ImageField(
        upload_to="recruiter/profile/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name or self.user.email}"


class OTP(models.Model):

    """
    OTP for verification and password reset.
    Purpose can be 'REGISTRATION' or 'RESET' etc.
    """
    PURPOSE_CHOICES = (
        ("REGISTRATION", "Registration"),
        ("RESET", "Reset"),
        ("OTHER", "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES, default="REGISTRATION")
    created_at = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["email", "purpose"]),
        ]

    def is_expired(self, ttl_seconds: int = 300) -> bool:
        return (timezone.now() - self.created_at).total_seconds() > ttl_seconds

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        return "".join(random.choices(string.digits, k=length))

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.code}"
