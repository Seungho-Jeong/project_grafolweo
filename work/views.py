import json

from django.http        import JsonResponse, HttpResponse
from django.views       import View

from work.models        import Category, Work, WorkImage, Comment, LikeIt, LikeItKind, CommentLike
from user.models        import User, Follow

class WorkDetailView(View):
    def get(self, request, work_id):

        try:
            this_work     = Work.objects.get(id = work_id)
            creator       = this_work.user
            related_works = creator.work_set.exclude(id = work_id)
            comments      = this_work.comment_set.all()
            detail        = {
                "id"          : this_work.id,
                "title"       : this_work.title,
                "article"     : this_work.article,
                "creator"     : this_work.user.user_name,
                "creator_img" : this_work.user.profile_image_url,
                "views"       : this_work.views,
                "created_at"  : this_work.created_at,
                "updated_at"  : this_work.updated_at,
                "image_url"   : [ workimage.image_url for workimage in this_work.workimage_set.all() ],
                "tag"         : [ tag.name for tag in this_work.tag.all() ],
                "commentNum"  : comments.count(),
                "comment"     : [ {
                    "id"               : comment.id,
                    "user_name"        : comment.user.user_name,
                    "profile_image_url": comment.user.profile_image_url,
                    "comment_content"  : comment.comment_content,
                    "created_at"       : comment.created_at
                    } for comment in comments ],
                "likeBtnNum"  : this_work.likeit_set.all().count(),
                "likeNum"     : this_work.likeit_set.filter(like_it_kind_id = 1).count(),
                "touchNum"    : this_work.likeit_set.filter(like_it_kind_id = 2).count(),
                "wantToBuyNum": this_work.likeit_set.filter(like_it_kind_id = 3).count(),
                "followerNum" : Follow.objects.filter(creator_id = creator.id).count(),
                "followingNum": Follow.objects.filter(follower_id = creator.id).count(),
                "others"      : [ {
                    "related_title"    : related_work.title,
                    "related_image_url": related_work.workimage_set.first().image_url
                    } for related_work in related_works ],
            }
            return JsonResponse({"artworkDetails": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

class CommentView(View):
    def post(self, request, work_id):
        data = json.loads(request.body)

        try:
            if not Work.objects.filter(id = work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

            Comment.objects.create(
                work_id         = work_id,
                user_id         = data["user_id"],
                comment_content = data["comment_content"]
            )
            return JsonResponse({"MESSAGE": "COMMENT_SUCCESS"}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": f"{e}_IS_MISSING"}, status=400)

    def delete(self, requset, work_id, comment_id):

        try:
            if not Work.objects.filter(id = work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

            Comment.objects.get(id = comment_id).delete()
            return JsonResponse({"MESSAGE": "DELETE_SUCCESS"}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)

    def patch(self, request, work_id, comment_id):
        data = json.loads(request.body)

        try:
            if not Work.objects.filter(id = work_id).exists():
                return JsonResponse({"MESSAGE":"DOES_NOT_EXIST_PAGE"}, status=400)

            if Comment.objects.get(id = comment_id).user.id != data["user_id"]:
                return JsonResponse({"MESSAGE": "UNAUTHORIZAION"}, status=401)

            target                 = Comment.objects.get(id = comment_id)
            target.comment_content = data["comment_content"]
            target.save()
            return JsonResponse({"MESSAGE": "MODIFY_SUCCESS"}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)

class CommentLikeView(View):
    def post(self, request, work_id, comment_id):
        data = json.loads(request.body)

        try:
            user_id = data["user_id"]

            if CommentLike.objects.filter(
                comment_id = comment_id,
                user_id    = user_id
            ).exists():
                CommentLike.objects.filter(
                    comment_id = comment_id,
                    user_id    = user_id
                )[0].delete()
                count = CommentLike.objects.filter(comment_id = comment_id).count()
                return JsonResponse({"LIKE_COUNT": count}, status=200)

            CommentLike.objects.create(
                comment_id = comment_id,
                user_id    = user_id
            )
            count = CommentLike.objects.filter(comment_id = comment_id).count()
            return JsonResponse({"LIKE_COUNT": count}, status=201)

        except User.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_USER"}, status=401)

        except Exception as e:
            return JsonResponse({"MESSAGE": f"ERROR_{e}"}, status=400)

class LikeView(View):
    def post(self, request, work_id, like_it_kind_id):
        data = json.loads(request.body)

        try:
            user_id   = data["user_id"]
            kind_id   = like_it_kind_id
            kind_name = LikeItKind.objects.get(id = like_it_kind_id).name

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

                count = LikeIt.objects.filter(like_it_kind_id = kind_id).count()
                return JsonResponse({f"{kind_name}_CANCELED": count}, status=200)

            if LikeIt.objects.filter(
                work_id = work_id,
                user_id = user_id
            ).exists():
                target = LikeIt.objects.filter(
                    work_id = work_id,
                    user_id = user_id)[0]

                target.like_it_kind_id = kind_id
                target.save()

                count = LikeIt.objects.filter(like_it_kind_id = kind_id).count()
                return JsonResponse({f"CHANGED_TO_{kind_name}": count}, status=200)

            LikeIt.objects.create(
                work_id         = work_id,
                user_id         = user_id,
                like_it_kind_id = kind_id
            )

            count = LikeIt.objects.filter(like_it_kind_id = kind_id).count()
            return JsonResponse({f"{kind_name}": count}, status=201)

        except Exception as e:
            return JsonResponse({"MESSAGE": f"ERROR{e}"}, status=400)
