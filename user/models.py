from django.db import models

class User(models.Model):
    user_name       = models.CharField(max_length = 40)
    email           = models.CharField(max_length = 50)
    mobile          = models.CharField(max_length = 40)
    password        = models.CharField(max_length = 100)
    profile_image   = models.CharField(max_length = 1000, null = True)
    short_introduce = models.CharField(max_length = 100, null = True)
    following       = models.ManyToManyField(
        'self',
        symmetrical = False,
        through     = "Follow",
        related_name= "follows" # Following과 겹치지 않게 테스트 후 변경 가능
    )

    class Meta:
        db_table = "Users"

class Follow(models.Model):
    follower        = models.ForeignKey("User", on_delete = models.CASCADE, related_name = "follower")
    creator         = models.ForeignKey("User", on_delete = models.CASCADE, related_name = "creator")

    class Meta:
        db_table = "Follows"

