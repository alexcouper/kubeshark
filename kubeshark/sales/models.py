from django.db import models

# Create your models here.
class KnownKubeShark(models.Model):
    email_address = models.CharField(max_length=30)
    created = models.DateField(auto_now_add=True)
