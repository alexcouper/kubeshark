from django.db import models

# Create your models here.
class KnownKubeShark(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
