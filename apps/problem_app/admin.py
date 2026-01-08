from django.contrib import admin
from .models import Problem , TestCases
# Register your models here.


class TestCaseInline(admin.TabularInline):
    model = TestCases
    extra = 1
    

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("title", "difficulty", "created_at")
    inlines = [TestCaseInline]


