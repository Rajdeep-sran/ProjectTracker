from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)  # Optional end date

    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # For sorting
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress(self):
        total = self.milestones.count()
        if total == 0:
            return 0
        completed = self.milestones.filter(is_completed=True).count()
        return int((completed / total) * 100)

    @property
    def status(self):
        total = self.milestones.count()
        if total == 0:
            return "Not Started"
        completed = self.milestones.filter(is_completed=True).count()
        if completed == 0:
            return "Not Started"
        elif completed < total:
            return "In Progress"
        else:
            return "Completed"


    def __str__(self):
        return self.title
    
class Milestone(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=100)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
