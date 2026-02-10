from django.db import models
from django.conf import settings
# Create your models here.


User = settings.AUTH_USER_MODEL

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('REMOTE', 'Remote'),
        ('ONSITE', 'Onsite'),
        ('HYBRID', 'Hybrid'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    ]

    recruiter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job' 
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    skills = models.JSONField()
    experience = models.PositiveIntegerField()
    responsibilities = models.JSONField(default=list)
    min_salary = models.PositiveIntegerField(default=0)
    max_salary = models.PositiveIntegerField(default=0)
    work_time = models.CharField(max_length=50, default='full-time')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Application(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('SHORTLISTED', 'Shortlisted'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
    )

    name = models.CharField(max_length=200)
    email = models.EmailField()
    contactNo = models.CharField(max_length=20)
    location = models.CharField(max_length=100)

  
    education = models.JSONField()
    workExperience = models.JSONField(null=True, blank=True)
    links = models.JSONField(null=True, blank=True)
    aboutYourself = models.TextField()
    skills = models.JSONField()

   
    resume = models.FileField(upload_to='applications/resumes/', null=True, blank=True)
    plusTwoCertificate = models.FileField(upload_to='applications/certificates/', null=True, blank=True)
    degreeCertificate = models.FileField(upload_to='applications/certificates/', null=True, blank=True)
    pgCertificate = models.FileField(upload_to='applications/certificates/', null=True, blank=True)

    
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['job', 'user']  # Prevent duplicate applications

    def __str__(self):
        return f"{self.name} - {self.job.title}"





