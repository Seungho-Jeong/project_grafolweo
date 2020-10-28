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

    @login_decorator
    def get(self, request) :
        sort        = request.GET.get('sort','')
        limit       = int(request.GET.get('limit','9'))
        offset      = int(request.GET.get('offset','0'))
        category_id = request.GET.get('category_id',None)
        sort_order  = [ { 
            '최신'     : '-created_at',
            '주목받는' : '-views'
        }, {
            '발견'     : 'Likes',
            '데뷰'     : 'singup_time'
        } ]
        if sort == "피드":
            works = [ work for creators in request.user.following.all() for work in creators.work_set.all()][offset:(offset+limit)]
        elif category_id :
            works = Work.objects.filter(category__id=category_id).select_related("user").prefetch_related("workimage_set", "likeit_set", "comment_set")
        else :
            works = Work.objects.all().select_related("user").prefetch_related("workimage_set", "likeit_set", "comment_set")
        if sort in sort_order[0] :
            works = works.order_by(sort_order[0][sort])[offset:(offset+limit)]

        workslist = [ {
                "id"            : work.id,
                "AuthorName"    : work.user.user_name,
                "AuthorProfile" : work.user.profile_image_url,
                "PostName"      : work.title,
                "Img"           : work.workimage_set.first().image_url,
                "Likes"         : work.likeit_set.count(),
                "Comments"      : work.comment_set.count(),
                "Views"         : work.views,
                "singup_time"   : work.user.created_at
            } for work in works ]
        if sort in sort_order[1] :
            workslist=sorted(workslist, reverse=True, key=lambda x: x[sort_order[1][sort]])[offset:(offset+limit)]
        return JsonResponse({'data': workslist }, status=200)

class CategoryListView(View) :
    
    def get(self, request) :
        categorylist = [ {
            "categoryid"      : category.id,
            "categoryName"    : category.name,
            "categoryCount"   : category.work_set.count(),
            "backgroundColor" : category.backgroundcolor,
            "image_url"       : category.image_url
        } for category in Category.objects.all().prefetch_related("work_set") ]
        return JsonResponse({'data': categorylist }, status=200)

class CategoryTagView(View) : 

    def get(self, request) :
        category_id        = request.GET.get('category_id')
        categories_to_tags = CategoryToTag.objects.filter( category_id = category_id).select_related("tag", "category")
        if categories_to_tags :
            taglist = [ {
                "id"        : category_to_tag.tag.id ,
                "name"      : category_to_tag.tag.name ,
                "image_url" : category_to_tag.category.image_url
            } for category_to_tag in categories_to_tags ]
            return JsonResponse({'listBannerTags': taglist }, status=200)
        else :
            return JsonResponse({'MESSAGE': "wrong category" }, status=400)

class PopularCreatorView(View) :

    def get(self, request) :
        category_id = int(request.GET.get('category_id'))
        users       = User.objects.all().prefetch_related("work_set", "user_to_follow")
        creatorlist = [{
                "id"            : user.id,
                "profileImgSrc" : user.profile_image_url,
                "name"          : user.user_name,
                "desc"          : user.introduction,
                "follower"      : user.user_to_follow.count(),
                "like"          : sum([ works.likeit_set.count() for works in user.work_set.all() ]),
                "illust"        : user.work_set.count(),
                "imgPreviewSrc" : [works.workimage_set.first().image_url for works in user.work_set.all()][:3],
                "category_like" : sum([ works.likeit_set.count() for works in user.work_set.all() if works.category.id == category_id ])
            } for user in users ]
        creatorlist = sorted(creatorlist, reverse=True, key=lambda x: x["category_like"])[:16]
        return JsonResponse({'popularCreator': creatorlist }, status=200)
