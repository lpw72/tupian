from django.db import models
from users.models import CustomUser

class File(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True)
    url = models.URLField()

    def __str__(self):
        return self.description