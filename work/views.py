import json
from django.http  import JsonResponse 
from django.views import View
from user.models  import User, Follow
from work.models  import (
    Category,
    Work,
    WorkImage,
    ThemeColor,
    WallpaperImage,
    LikeItKind,
    LikeIt,
    Tag,
    CategoryToTag,
    WorkToTag,
    Comment,
    CommentLike,
    Reply,
    ReplyLike
)
