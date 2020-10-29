
import random
import json

from django.http    import JsonResponse
from django.views   import View

from django.db      import IntegrityError
from user.utils     import login_decorator
from user.models    import User, Follow
from work.models    import (
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

class WorkDetailView(View):
    @login_decorator
    def get(self, request, work_id):
        this_work     = Work.objects.select_related("user").get(id = work_id)
        this_work.views += 1
        this_work.save()

        comments      = Comment.objects.filter(work_id = work_id).select_related("work")
        related_works = this_work.user.work_set.exclude(id = work_id)
        like_it_kinds = LikeItKind.objects.all()

        try:
            detail    = {
                "id"          : this_work.id,
                "title"       : this_work.title,
                "article"     : this_work.article,
                "creator"     : this_work.user.user_name,
                "creator_id"  : this_work.user.id,
                "creator_img" : this_work.user.profile_image_url,
                "user_id"     : request.user.id if request.user else "GEUST",
                "user_name"   : request.user.user_name if request.user else "GEUST",
                "user_image"  : request.user.profile_image_url if request.user else "GEUST",
                "views"       : this_work.views,
                "created_at"  : this_work.created_at,
                "updated_at"  : this_work.updated_at,
                "image_url"   : [ workimage.image_url for workimage in this_work.workimage_set.all() ],
                "tag"         : [ tag.name for tag in this_work.tag.all() ],
                "commentNum"  : comments.count(),
                "likeBtnNum"  : LikeIt.objects.filter(work_id = work_id).count(),
                "followerNum" : this_work.user.creator.all().count(),
                "followingNum": this_work.user.follower.all().count(),
                "comment"     : [ {
                    "comment_id"        : comment.id,
                    "commenter_name"    : comment.user.user_name,
                    "commenter_image"   : comment.user.profile_image_url,
                    "comment_content"   : comment.comment_content,
                    "comment_created_at": comment.created_at
                    } for comment in comments ],
                "likeIt"      : [ {
                    f"like_id_{kind.id}": LikeIt.objects.filter(
                        work_id         = work_id,
                        like_it_kind_id = kind
                    ).count()} for kind in like_it_kinds.all()],
                "others"      : [ {
                    "related_title"     : related_work.title,
                    "related_image_url" : related_work.workimage_set.first().image_url
                    } for related_work in related_works ]
            }
            return JsonResponse({"artworkDetails": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

class CommentView(View):
    @login_decorator
    def post(self, request, work_id):
        data = json.loads(request.body)

        try:
            if not User.objects.filter(id = request.user.id).exists():
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            if not Work.objects.filter(id = work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

            Comment.objects.create(
                work_id         = work_id,
                user_id         = request.user.id,
                comment_content = data["comment_content"]
            )
            return JsonResponse({"MESSAGE": "COMMENT_SUCCESS"}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": f"{e}_IS_MISSING"}, status=400)

    @login_decorator
    def delete(self, request, work_id, comment_id):

        try:
            comment = Comment.objects.get(id = comment_id, work_id = work_id)
            comment.delete()
        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)

    @login_decorator
    def patch(self, request, work_id, comment_id):
        data = json.loads(request.body)

        try:
            if not Work.objects.filter(id = work_id).exists():
                return JsonResponse({"MESSAGE":"DOES_NOT_EXIST_PAGE"}, status=400)

            if Comment.objects.get(id = comment_id).user.id != request.user.id:
                return JsonResponse({"MESSAGE": "UNAUTHORIZAION"}, status=401)

            target                 = Comment.objects.get(id = comment_id)
            target.comment_content = data["comment_content"]
            target.save()
            return JsonResponse({"MESSAGE": "MODIFY_SUCCESS"}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)

class CommentLikeView(View):
    @login_decorator
    def post(self, request, work_id, comment_id):
        data = json.loads(request.body)
        like = data["like"]

        try:
            if CommentLike.objects.filter(
                comment_id = comment_id,
                user_id    = request.user.id
            ).exists():
                CommentLike.objects.filter(
                    comment_id = comment_id,
                    user_id    = request.user.id
                )[0].delete()
                count = CommentLike.objects.filter(comment_id = comment_id).count()
                return JsonResponse({"CANCEL_SUCCESS": count}, status=200)

            CommentLike.objects.create(
                comment_id = comment_id,
                user_id    = request.user.id
            )
            count = CommentLike.objects.filter(comment_id = comment_id).count()
            return JsonResponse({"LIKEIT_SUCCESS": count}, status=201)

        except User.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_USER"}, status=401)

class LikeView(View):
    @login_decorator
    def post(self, request, work_id):
        data    = json.loads(request.body)
        user_id = request.user.id

        try:
            like_it_kinds   = LikeItKind.objects.all()
            kind_id   = data["like_it_kind_id"]
            if LikeIt.objects.filter(
                work_id         = work_id,
                user_id         = user_id,
                like_it_kind_id = kind_id
            ).exists():
                LikeIt.objects.filter(
                    work_id         = work_id,
                    user_id         = user_id,
                    like_it_kind_id = kind_id
                )[0].delete()

                likeIt = [ {
                    f"like_id_{kind.id}": LikeIt.objects.filter(
                        work_id         = work_id,
                        like_it_kind_id = kind
                    ).count()} for kind in like_it_kinds.all() ]
                return JsonResponse({"CANCEL_SUCCESS": likeIt}, status=200)

            if LikeIt.objects.filter(
                work_id = work_id,
                user_id = user_id
            ).exists():
                target = LikeIt.objects.filter(
                    work_id = work_id,
                    user_id = user_id)[0]

                target.like_it_kind_id = kind_id
                target.save()

                likeIt = [ {
                    f"like_id_{kind.id}": LikeIt.objects.filter(
                        work_id         = work_id,
                        like_it_kind_id = kind
                    ).count()} for kind in like_it_kinds.all() ]
                return JsonResponse({"CHANGE_SUCCESS": likeIt}, status=200)

            LikeIt.objects.create(
                work_id         = work_id,
                user_id         = user_id,
                like_it_kind_id = kind_id
            )

            likeIt = [ {
                f"like_id_{kind.id}": LikeIt.objects.filter(
                    work_id         = work_id,
                    like_it_kind_id = kind
                ).count()} for kind in like_it_kinds.all() ]
            return JsonResponse({"LIKEIT_SUCCESS": likeIt}, status=201)

        except Exception as e:
            return JsonResponse({"MESSAGE": f"ERROR{e}"}, status=400)

class WallpaperDetailView(View):
    def get(self, request, wallpaper_id):
        try:
            this_wallpaper = WallpaperImage.objects.select_related("work").get(id = wallpaper_id)
            creator        = this_wallpaper.work.user
            detail         = {
                "id"            : this_wallpaper.id,
                "title"         : this_wallpaper.work.title,
                "creator"       : this_wallpaper.work.user.user_name,
                "creator_img"   : this_wallpaper.work.user.profile_image_url,
                "views"         : this_wallpaper.work.views,
                "created_at"    : this_wallpaper.work.created_at,
                "image_url"     : this_wallpaper.image_url,
                "themecolor_id" : this_wallpaper.themecolor_id,
                "downloadNum"   : this_wallpaper.download_count,
                "tag"           : [ tag.name for tag in this_wallpaper.work.tag.all() ],
            }
            return JsonResponse({"wallpaperDetails": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

class TopCreatorsView(View) :

    @login_decorator
    def get(self, request) :
        CONST_LENGTH = 9
        creators    = User.objects.all().prefetch_related('work_set')
        creatorlist = [ {
            "id"                : creator.id,
            "user_name"         : creator.user_name,
            "profile_image_url" : creator.profile_image_url,
            "followBtn"         : creator.creator.filter(follower_id=request.user.id).exists() if request.user else False,
            "likecount"         : sum([ work.likeit_set.count() for work in creator.work_set.all() ]),
        } for creator in creators ]
        creatorlist = sorted(creatorlist, reverse=True, key=lambda x: x["likecount"])[:CONST_LENGTH]
        return JsonResponse({'topCreators': creatorlist }, status=200)

class FollowView(View) :

    @login_decorator
    def post(self, request) :
        if request.user :
            try :
                data       = json.loads(request.body)
                user_id    = request.user.id
                creator_id = data['creator_id']
                follow     = Follow.objects.get(follower_id = user_id, creator_id = creator_id)
                follow.delete()
                data = {
                    "id"        : creator_id,
                    "followBtn" : False
                }
                return JsonResponse({'data': data }, status=201)
            except Follow.DoesNotExist :
                try :
                    Follow.objects.create( follower_id = user_id, creator_id = creator_id)
                    data = {
                        "id"        : creator_id,
                        "followBtn" : True
                    }
                    return JsonResponse({'data': data }, status=201)
                except IntegrityError :
                    return JsonResponse({'MESSAGE': "Error: unknown user" }, status=400)
            except KeyError as e :
                return JsonResponse({'MESSAGE': f"KeyError: {e}" }, status=400)
            except json.decoder.JSONDecodeError :
                return JsonResponse({'MESSAGE': "Error: json data error" }, status=400)
        return JsonResponse({'MESSAGE': "Need login" }, status=400)

    @login_decorator
    def get(self, request) :
        creator_id = request.GET.get('creator_id')
        following  = Follow.objects.filter(follower_id = request.user.id, creator_id = creator_id).exists() if request.user else False
        data = {
            "creator_id" : creator_id,
            "followBtn"  : following
        }
        return JsonResponse({'data': data }, status=200)

class EditorPickWallpaperView(View) :

    def get(self, request) :
        CONST_LENGTH = 8
        tag_id       = request.GET.get('tag')
        if tag_id :
            wallpaper_post = Work.objects.filter(tag__id=tag_id).select_related('user').prefetch_related("wallpaperimage_set")
        else :
            taglistall      = [ {
                "id"   : tag.id ,
                "name" : tag.name
            } for tag in Tag.objects.all() if not tag.category_tag.exists() ]
            taglist         = random.sample(taglistall, 5)
            first_tag       = taglist[0]["id"]
            wallpaper_post = Work.objects.filter(tag__id=first_tag).select_related('user').prefetch_related("wallpaperimage_set")

        slides    = [ {
            "wallpaper_id"  : work.wallpaperimage_set.first().id ,
            "subject"       : work.title ,
            "wallpaperSrc"  : work.wallpaperimage_set.first().image_url ,
            "name"          : work.user.user_name ,
            "profileImgSrc" : work.user.profile_image_url,
            "downloadNum"   : work.wallpaperimage_set.first().download_count
        } for work in wallpaper_post if work.wallpaperimage_set.exists() ][:CONST_LENGTH]
        if tag_id :
            return JsonResponse({'editorsPickData': { "Slides"  : slides
            } }, status=200)
        else :
            return JsonResponse({'editorsPickData': {
                "TagList" : taglist,
                "Slides"  : slides
            } }, status=200)

class WallpaperCardListView(View) :

    def get(self, request) :

        def cardlist(works) :
            if order =='최신순':
                works = works.order_by('-created_at')
            cardlist = [ {
                    "wallpaper_id"  : work.wallpaperimage_set.first().id ,
                    "subject"       : work.title ,
                    "wallpaperSrc"  : work.wallpaperimage_set.first().image_url ,
                    "name"          : work.user.user_name ,
                    "profileImgSrc" : work.user.profile_image_url,
                    "downloadNum"   : work.wallpaperimage_set.first().download_count,
                    "views"         : work.views,
                    "created_at"    : work.created_at
                } for work in works if work.wallpaperimage_set.exists() ]
            if order =='인기순' :
                cardlist = sorted(cardlist, reverse=True, key=lambda x: x["downloadNum"])
            return cardlist

        limit     = int(request.GET.get('limit','9'))
        offset    = int(request.GET.get('offset','0'))
        sort_name = request.GET.get('sort')
        order     = request.GET.get('order')
        id        = request.GET.get('id')
        filter = {
            '태그별' : [Work.objects.filter(tag__id = id).select_related('user').prefetch_related("wallpaperimage_set"),"discoverTagData"],
            '색상별' : [Work.objects.filter(wallpaperimage__themecolor_id = id).select_related('user').prefetch_related("wallpaperimage_set"),"discoverColorData"],
            '유형별' : [Work.objects.filter(category__id = id).select_related('user').prefetch_related("wallpaperimage_set"),"discoverTypeData"]
        }
        try :
            if not id and sort_name == "태그별" :
                tag_list = [ {
                    "id"   : tag.id,
                    "name" : tag.name
                } for tag in Tag.objects.all() if not tag.category_tag.exists() ][:10]
                taglist = [ { "id" : 0, "name" : "전체" } ] + tag_list
                works   = Work.objects.all().select_related('user').prefetch_related("wallpaperimage_set")
                cardviewlist = cardlist(works)[offset:(offset+limit)]
                return JsonResponse({'discoverTagData': {
                    "tagList"      : taglist,
                    "cardViewList" : cardviewlist
                } }, status=200)

            elif id == '0' and sort_name == "태그별" :
                works        = Work.objects.all().select_related('user').prefetch_related("wallpaperimage_set")
            elif id :
                works = filter[sort_name][0]
            else :
                return JsonResponse({'Error': "Need id" }, status=400)
            if works :
                cardviewlist = cardlist(works)[offset:(offset+limit)]
                return JsonResponse({filter[sort_name][1]: {"cardViewList" : cardviewlist} }, status=200)
            else :
                return JsonResponse({'Error': "Invalid id" }, status=400)
        except KeyError :
            return JsonResponse({'Error': "Invalid sort_name" }, status=400)

class WallpaperdownloadcountView(View) :

    def post(self, request) :
        data              = json.loads(request.body)
        WallpaperImage_id = data['wallpaper_id']
        try :
            wallpaper    = WallpaperImage.objects.get(id= WallpaperImage_id)
            wallpaper.download_count += 1
            wallpaper.save()
            return JsonResponse({
                'MESSAGE'     : "Download Count Success",
                "image_url"   : wallpaper.image_url,
                "downloadNum" : wallpaper.download_count
            }, status=200)
        except WallpaperImage.DoesNotExist :
            return JsonResponse({'Error': "Invalid wallpaper_id" }, status=400)

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

