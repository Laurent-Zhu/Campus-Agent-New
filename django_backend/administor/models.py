from django.db import models
from django.contrib.auth.models import User

class Subject(models.Model):
    name = models.CharField(max_length=50, verbose_name='学科名称')

class Resource(models.Model):
    RESOURCE_TYPES = (
        ('ppt', 'PPT'),
        ('exercise', '练习题'),
        ('video', '视频'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='resources/%Y/%m/')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    shared = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'administor_resource'

# Create your models here.
