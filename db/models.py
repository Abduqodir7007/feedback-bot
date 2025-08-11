import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Feedback(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=64)
    feedback = models.TextField()
    user_id = models.PositiveIntegerField()
    
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'