from django.db      import models
from user.models    import User

class Category(models.Model):
    name            = models.CharField(max_length = 40)
    backgroundcolor = models.CharField(max_length = 40)
    image_url       = models.URLField(max_length = 1000)
    tag             = models.ManyToManyField("Tag", through = "CategoryToTag", related_name = "categories_tags")

    class Meta:
        db_table = "categories"

class Work(models.Model):
    user       = models.ForeignKey("user.User", on_delete = models.CASCADE)
    category   = models.ForeignKey(Category, on_delete = models.CASCADE)
    title      = models.CharField(max_length = 100)
    article    = models.TextField(null = True)
    views      = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    tag        = models.ManyToManyField("Tag", through = "WorkToTag", related_name = "works_tags")

    class Meta:
        db_table = "works"

class WorkImage(models.Model):
    work      = models.ForeignKey(Work, on_delete = models.CASCADE)
    image_url = models.URLField(max_length = 1000)

    class Meta:
        db_table = "works_images"

class ThemeColor(models.Model):
    name = models.CharField(max_length = 40)

    class Meta:
        db_table = "theme_colors"

class WallpaperImage(models.Model):
    work           = models.ForeignKey(Work, on_delete = models.CASCADE)
    themecolor     = models.ForeignKey(ThemeColor, on_delete = models.CASCADE)
    image_url      = models.URLField(max_length = 1000)
    download_count = models.IntegerField(default = 0)

    class Meta:
        db_table = "wall_paper_images"

class LikeItKind(models.Model):
    name = models.CharField(max_length = 40)

    class Meta:
        db_table = "like_it_kinds"

class LikeIt(models.Model):
    user         = models.ForeignKey("user.User", on_delete = models.CASCADE)
    work         = models.ForeignKey(Work, on_delete = models.CASCADE)
    like_it_kind = models.ForeignKey(LikeItKind, on_delete = models.CASCADE)

    class Meta:
        db_table = "like_it"

class Tag(models.Model):
    name            = models.CharField(max_length = 40)

    class Meta:
        db_table = "tags"

class CategoryToTag(models.Model):
    category        = models.ForeignKey(Category, on_delete = models.CASCADE, related_name = "category")
    tag             = models.ForeignKey(Tag, on_delete = models.CASCADE, related_name = "category_tag")

    class Meta:
        unique_together = ("category", "tag")
        db_table        = "categories_tags"

class WorkToTag(models.Model):
    work            = models.ForeignKey(Work, on_delete = models.CASCADE, related_name = "work")
    tag             = models.ForeignKey(Tag, on_delete = models.CASCADE, related_name = "work_tag")

    class Meta:
        unique_together = ("work", "tag")
        db_table        = "works_tags"

class Comment(models.Model):
    user            = models.ForeignKey("user.User", on_delete = models.CASCADE)
    work            = models.ForeignKey(Work, on_delete = models.CASCADE)
    comment_content = models.CharField(max_length = 1000)
    created_at      = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = "comments"

class CommentLike(models.Model):
    user    = models.ForeignKey("user.User", on_delete = models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete = models.CASCADE)

    class Meta:
        db_table = "comment_likes"

class Reply(models.Model):
    user          = models.ForeignKey("user.User", on_delete = models.CASCADE)
    comment       = models.ForeignKey(Comment, on_delete = models.CASCADE)
    reply_content = models.CharField(max_length = 1000)
    created_at    = models.DateTimeField(auto_now_add = True)

    class Meta:
        db_table = "replies"

class ReplyLike(models.Model):
    user  = models.ForeignKey("user.User", on_delete = models.CASCADE)
    reply = models.ForeignKey(Reply, on_delete = models.CASCADE)

    class Meta:
        db_table = "reply_likes"
