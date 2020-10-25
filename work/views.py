import json
from django.http  import JsonResponse 
from django.views import View
from django.db    import IntegrityError
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

class TopCreatorsView(View) :
    
    def get(self, request) : 
        user_id     = 10    # 임시 데이터, 추후 토큰 데코레이터를 통해 user_id 받을 예정
        creators    = User.objects.all()
        creatorlist = [ {
            "id"                : creator.id,
            "user_name"         : creator.user_name,
            "profile_image_url" : creator.profile_image_url,
            "followBtn"         : creator.creator.filter(follower_id=user_id).exists()
        } for creator in creators ][:9]
        return JsonResponse({'topCreators': creatorlist }, status=200)

class WallpaperMainFollowView(View) :
    
    def post(self, request) : 
        try :
            data       = json.loads(request.body) 
            user_id    = 10    # 임시 데이터, 추후 토큰 데코레이터를 통해 user_id 받을 예정
            creator_id = data['creator_id']
            follow     = Follow.objects.get(follower_id = user_id, creator_id = creator_id)
            follow.delete()
            message = {
                "id"        : creator_id,
                "followBtn" : False
            }
            return JsonResponse({'data': message }, status=200)
        except Follow.DoesNotExist :
            try :
                Follow.objects.create( follower_id = user_id, creator_id = creator_id)
                message = {
                    "id"        : creator_id,
                    "followBtn" : True
                }
                return JsonResponse({'data': message }, status=200)
            except IntegrityError :
                return JsonResponse({'Error': "unknown user" }, status=400)
        except KeyError as e :
            return JsonResponse({'Key Error': str(e) }, status=400)
        except json.decoder.JSONDecodeError :
            return JsonResponse({'Error': "json data error" }, status=400)