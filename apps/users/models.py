import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    
    role = models.CharField(max_length=50, default="user")
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True, blank=True)
    
    
    def __str__(self):
        return self.username