import json

from django.http        import JsonResponse, HttpResponse
from django.views       import View

from user.utils         import login_decorator
from user.models        import User, Follow
from work.models        import (
    Category,
    Work,
    WorkImage,
    Comment,
    LikeIt,
    LikeItKind,
    CommentLike,
)

class WorkDetailView(View):
    @login_decorator
    def get(self, request, work_id):
        this_work     = Work.objects.select_related("user").get(id = work_id)
        this_work.views += 1
        this_work.save()

        comments      = Comment.objects.filter(work_id = work_id).prefetch_related("work")
        related_works = Work.objects.filter(user_id = this_work.user.id).exclude(id = work_id)
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
                "user_name"   : User.objects.get(id=request.user.id).user_name if request.user else "GEUST",
                "user_image"  : User.objects.get(id=request.user.id).profile_image_url if request.user else "GEUST",
                "views"       : this_work.views,
                "created_at"  : this_work.created_at,
                "updated_at"  : this_work.updated_at,
                "image_url"   : [ workimage.image_url for workimage in this_work.workimage_set.all() ],
                "tag"         : [ tag.name for tag in this_work.tag.all() ],
                "commentNum"  : comments.count(),
                "likeBtnNum"  : LikeIt.objects.filter(work_id = work_id).count(),
                "followerNum" : Follow.objects.filter(creator_id = this_work.user.id).count(),
                "followingNum": Follow.objects.filter(follower_id = this_work.user.id).count(),
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
