import json
from django.http  import JsonResponse 
from django.views import View
from user.models  import User, Follow
from work.models  import (
    Category,
    Work,
    WorkImage,
    WallpaperImage,
    LikeIt,
    Tag,
    CategoryToTag,
    Comment,
    CommentLike,
    Reply,
    ReplyLike
)

class WorksListView(View) :

    def get(self, request) :
        sort       = request.GET.get('sort')
        limit      = int(request.GET.get('limit'))
        offset     = int(request.GET.get('offset'))
        sort_order = { 
            '최신'     : '-created_at',
            '주목받는' : '-views'
        }

        if sort in sort_order :
            works = Work.objects.all().order_by(sort_order[sort]).select_related("user").prefetch_related("workimage_set", "likeit_set", "comment_set")[offset:(offset+limit)]
        elif sort == "발견" or sort == "데뷰" :
            works = Work.objects.all().select_related("user").prefetch_related("workimage_set", "likeit_set", "comment_set")
        else :
            return JsonResponse({'MESSAGE':'Invalid sorted name'}, status=400)

        workslist = [ {
                "id"            : work.id ,
                "AuthorName"    : work.user.user_name ,
                "AuthorProfile" : work.user.profile_image_url ,
                "PostName"      : work.title ,
                "Img"           : work.workimage_set.first().image_url,
                "Likes"         : work.likeit_set.count(),
                "Comments"      : work.comment_set.count(),
                "Views"         : work.views,
                "singup_time"   : work.user.created_at
            } for work in works ]
        if sort == "발견" :
            workslist=sorted(workslist, reverse=True, key=lambda x: x["Likes"])[offset:(offset+limit)]
            return JsonResponse({'data': workslist }, status=200)
        elif sort == "데뷰" :
            workslist=sorted(workslist, reverse=True, key=lambda x: x["singup_time"])[offset:(offset+limit)]
            return JsonResponse({'data': workslist }, status=200)
        else :
            return JsonResponse({'data': workslist }, status=200)

class CategoryListView(View) :
    
    def get(self, request) :
        categorylist = [ {
            "categoryid"      : category.id,
            "categoryName"    : category.name,
            "categoryCount"   : category.work_set.count(),
            "backgroundColor" : category.backgroundcolor,
            "image_url"       : category.image_url
        } for category in Category.objects.all() ]
        return JsonResponse({'data': categorylist }, status=200)

class CategoryTagView(View) : 

    def get(self, request, category_id) :
        try :
            categories_to_tags = CategoryToTag.objects.filter( category_id = category_id).select_related("tag")
            taglist = [ {
                "id" : category_to_tag.tag.id ,
                "name" : category_to_tag.tag.name 
            } for category_to_tag in categories_to_tags ]
            return JsonResponse({'listBannerTags': taglist }, status=200)
        except Category.DoesNotExist :
            return JsonResponse({'MESSAGE': "wrong category" }, status=400)

class PopularCreatorView(View) :

    def get(self, request) :
        category    = request.GET.get('category')
        users       = User.objects.all().prefetch_related("work_set", "user_to_follow")
        creatorlist = [{
                "id"            : user.id,
                "profileImgSrc" : user.profile_image_url,
                "name"          : user.user_name,
                "desc"          : user.introduction,
                "follower"      : user.user_to_follow.count(),
                "like"          : sum([ works.likeit_set.count() for works in user.work_set.all() ]),
                "illust"        : user.work_set.count(),
                "imgPreviewSrc" : [works.workimage_set.all()[0].image_url for works in user.work_set.all()][:3],
                "category_like" : sum([ works.likeit_set.count() for works in user.work_set.all() if works.category.name == category ])
            } for user in users ]
        creatorlist = sorted(creatorlist, reverse=True, key=lambda x: x["category_like"])[:16]
        return JsonResponse({'popularCreator': creatorlist }, status=200)
