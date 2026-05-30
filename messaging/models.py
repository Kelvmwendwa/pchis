from django.db import models
from django.conf import settings


class Message(models.Model):

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')

    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)


    is_delivered = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"