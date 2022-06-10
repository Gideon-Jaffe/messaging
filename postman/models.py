from django.utils import timezone
from django.db import models
from django.conf import settings

# Create your models here.
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reciever")
    message = models.CharField(max_length=80)
    subject = models.CharField(max_length=20)
    creation_date = models.DateTimeField('date sent', default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.message}"
