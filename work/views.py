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

    def get(self, request, sort, page) :
        if sort == "최신" :
            work_all = Work.objects.all().order_by('-created_at')
            work_all = work_all[12*(page-1):12*page]
        elif sort == "주목받는" :
            work_all = Work.objects.all().order_by('-views')
            work_all = work_all[12*(page-1):12*page]
        elif sort == "발견" :
            work_all = Work.objects.all()
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
                "Views"         : work.views
            } for work in work_all ]
        if sort == "발견" :
            workslist=sorted(workslist, reverse=True, key=lambda x: x["Likes"])[12*(page-1):12*page]
            return JsonResponse({'data': workslist }, status=200)
        else :
            return JsonResponse({'data': workslist }, status=200)

class MainCategoryView(View) :
    
    def get(self, request) :
        categorylist = [ {
            "categoryName"  : category.name,
            "categoryCount" : category.work_set.count()
        } for category in Category.objects.all() ]
        return JsonResponse({'data': categorylist }, status=200)

class CategoryTagView(View) : 

    def get(self, request, category) :
        try :
            category_id = Category.objects.get( name = category ).id
            categories_to_tags = CategoryToTag.objects.filter( category_id = category_id)
            taglist = [ {
                "id" : category_to_tag.tag.id ,
                "name" : category_to_tag.tag.name 
            } for category_to_tag in categories_to_tags ]
            return JsonResponse({'listBannerTags': taglist }, status=200)
        except KeyError :
            return JsonResponse({'MESSAGE': "wrong category" }, status=400)

class PopularCreatorView(View) :

    def get(self, request, category) :
        users = User.objects.all()
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