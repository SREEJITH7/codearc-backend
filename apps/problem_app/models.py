from django.db import models

# Create your models here.

class Category(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('InActive', 'InActive'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    DIFFICULTY_CHOICES = (
        ("EASY", "Easy"),
        ("MEDIUM", "Medium"),
        ("HARD", "Hard"),
    )

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, db_index=True)

    tags = models.JSONField(default=list)
    examples = models.JSONField(default=list)
    hints = models.JSONField(default=list)

    function_name = models.CharField(max_length=100)
    parameters = models.JSONField(default=list)
    return_type = models.CharField(max_length=50)

    constraints = models.JSONField(default=list, blank=True)

    solution = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="problems"
    )

    starter_code = models.JSONField(default=dict)
    supported_languages = models.JSONField(default=list)

    time_limit = models.IntegerField(default=2)
    memory_limit = models.IntegerField(default=256)

    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)

    total_submissions = models.IntegerField(default=0)
    accepted_submissions = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="problems"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    
class TestCases(models.Model):
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name="testcases"
    )
    input = models.JSONField()
    expected_output = models.JSONField()
    is_sample = models.BooleanField(default=False)

    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"TestCases for {self.problem.title}"
    
class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="companies/", blank=True, null=True)

    def __str__(self):
        return self.name

