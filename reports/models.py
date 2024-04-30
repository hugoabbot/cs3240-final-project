from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User


class Report(models.Model):
    STATUS_CHOICES = (
        ('New', 'New'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )

    # Fields for the report model
    report_text = models.TextField()
    report_file = models.FileField(upload_to='report_files/', blank=True, null=True)
    residence_type = models.CharField(max_length=100)
    report_type = models.CharField(max_length=100, blank=True)  # Add a default value
    residence = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True, null=True)  # Make it optional
    floor = models.IntegerField(blank=True, null=True)  # Make it optional
    room = models.CharField(max_length=100, blank=True, null=True)  # Make it optional
    submission_timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    admin_message = models.TextField(blank=True, null=True)  # New field for admin message

    def __str__(self):
        return f"Report #{self.id} - {self.status}"


class Residence(models.Model):
    residence_type = models.CharField(max_length=200)
    residence = models.CharField(max_length=200)
    building = models.CharField(max_length=200)

    def __str__(self):
        return self.building


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    residence = models.CharField(max_length=200, null=True)
    building = models.CharField(max_length=200, null=True)
    floor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_delete, sender=Report)
def remove_file_from_s3(sender, instance, **kwargs):
    if instance.report_file:
        instance.report_file.delete(save=False)
