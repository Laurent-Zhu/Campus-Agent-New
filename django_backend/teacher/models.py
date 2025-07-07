from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LessonPreparationRecord(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_time = models.DateTimeField(auto_now_add=True)
    outline_file = models.FileField(upload_to='lesson_preparation/')
    result_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.username} - {self.upload_time}"

# Create your models here.