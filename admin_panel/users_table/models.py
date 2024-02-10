from django.db import models

class User(models.Model):
    user_tgid = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    class Meta:
        db_table = "users"
