from django.db      import models

class User(models.Model):
    user_name         = models.CharField(max_length = 40)
    email             = models.CharField(max_length = 50)
    mobile            = models.CharField(max_length = 40)
    password          = models.CharField(max_length = 200)
    introduction      = models.CharField(max_length = 300, null = True)
    profile_image_url = models.URLField(max_length = 1000, null = True)
    created_at        = models.DateTimeField(auto_now_add = True)
    updated_at        = models.DateTimeField(auto_now = True)
    following         = models.ManyToManyField(
        "self", symmetrical = False, through = "Follow", related_name = "user_to_follow"
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.user_name

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "follower")
    creator  = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "creator")

    class Meta:
        unique_together = ("follower", "creator")
        db_table        = "follows"

    def __str__(self):
        return self.follower
