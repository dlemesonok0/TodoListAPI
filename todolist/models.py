from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField()
    done = models.BooleanField(default=False)
    date = models.DateTimeField()