from django.db import models

class User(models.Model):
    user_name           = models.CharField(max_length = 40)
    email               = models.CharField(max_length = 50)
    mobile              = models.CharField(max_length = 40)
    password            = models.CharField(max_length = 100)
    introduction        = models.CharField(max_length = 300, null = True)
    profile_image_url   = models.CharField(max_length = 1000, null = True)
    created_at          = models.DateTimeField(auto_now_add = True)
    updated_at          = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = "Users"
