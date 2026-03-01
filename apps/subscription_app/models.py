from django.db import models
from django.utils import timezone
from datetime import timedelta 
from django.contrib.auth import get_user_model

User = get_user_model()


class Plan(models.Model):
    ROLE_CHOICES = (
        ('USER', 'User'),
        ('RECRUITER', 'Recruiter'),
    )

    name = models.CharField(max_length=50)
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    stripe_price_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.role_type} - {self.name}"
    
class Subscription(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Payment'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('GRACE', 'Grace Period'),
        ('FAILED', 'Payment Failed'),
    )

    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )

    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    grace_end_date = models.DateTimeField(null=True, blank=True)

    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def activate(self):
        """
        Activate subscription after Stripe confirms payment.
        """
        now = timezone.now()
        self.status = 'ACTIVE'
        self.start_date = now
        self.end_date = now + timedelta(days=self.plan.duration_days)
        self.grace_end_date = self.end_date + timedelta(days=2)
        self.save()

    def mark_failed(self):
        self.status = 'FAILED'
        self.save()

    def move_to_grace(self):
        self.status = 'GRACE'
        self.save()

    def expire(self):
        self.status = 'EXPIRED'
        self.save()

    @property
    def is_active(self):
        return self.status == 'ACTIVE'

    @property
    def is_within_grace(self):
        if not self.grace_end_date:
            return False
        return timezone.now() <= self.grace_end_date

    def __str__(self):
        return f"{self.user} - {self.plan.name} - {self.status}"
    
class SubscriptionHistory(models.Model):
    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.CASCADE,
        related_name='subscription_history'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    reason = models.CharField(max_length=100, default='expired')

    class Meta:
        ordering = ['-ended_at']

    def __str__(self):
        return f"{self.user} - {self.plan.name} history"
    

class CodeRunUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey("Subscription", on_delete=models.CASCADE)
    run_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)