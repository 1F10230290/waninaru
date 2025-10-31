from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

# Create your models here.
s3_storage = S3Boto3Storage()

class DesignIdea(models.Model):
    image = models.ImageField(upload_to='aidea/', storage=s3_storage, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Idea {self.id}'
