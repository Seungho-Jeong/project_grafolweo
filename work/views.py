import json

from django.http        import JsonResponse, HttpResponse
from django.views       import View

from work.models        import Category, Work, WorkImage, Comment
from user.models        import User

class WorkDetailView(View):
    def get(self, request, work_id):

        try:
            this_work     = Work.objects.get(id = work_id)
            creator       = this_work.user
            related_works = creator.work_set.exclude(id = work_id)
            comments      = Comment.objects.filter(work_id = work_id)
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
                "commentNum"  : len(comments),
                "comment"     : [ {
                    "user_name"        : comment.user.user_name,
                    "profile_image_url": comment.user.profile_image_url,
                    "comment_content"  : comment.comment_content
                    } for comment in comments ],
                "others"      : [ {
                    "related_title"    : related_work.title,
                    "related_image_url": related_work.workimage_set.first().image_url
                    } for related_work in related_works ]
            }

            return JsonResponse({"artworkDetails": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)


class CommentView(View):
    def post(self, request, work_id):
        data = json.loads(request.body)

        try:
            if Work.objects.filter(id = work_id).exists():

                user_name       = data["user_name"]
                comment_content = data["comment_content"]
                user_id = User.objects.get(user_name = user_name).id

                Comment.objects.create(
                    work_id         = work_id,
                    user_id         = user_id,
                    comment_content = comment_content
                )

                comments = Comment.objects.filter(work_id = work_id)
                comment_list = [ {
                    "id"              : comment.id,
                    "user_name"       : comment.user.user_name,
                    "comment_content" : comment.comment_content,
                    "created_at"      : comment.created_at
                } for comment in comments ]

                return JsonResponse({"POSTING_SUCCESS": comment_list}, status=201)

            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=400)

        except KeyError as e:
            return JsonResponse({"MESSAGE": f"KEY_ERROR:{e}"}, status=400)

        except ValueError as e:
            return JsonResponse({"MESSAGE": f"VALUE_ERROR:{e}"}, status=400)


    def delete(self, requset, work_id, comment_id):

        try:
            Comment.objects.get(id = comment_id).delete()

            comments = Comment.objects.filter(work_id = work_id)
            comment_list = [ {
                "id"              : comment.id,
                "user_name"       : comment.user.user_name,
                "comment_content" : comment.comment_content,
                "created_at"      : comment.created_at
            } for comment in comments ]

            return JsonResponse({"DELETE_SUCCESS": comment_list}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)


    def patch(self, request, work_id, comment_id):
        data = json.loads(request.body)

        try:
            user_name   = data["user_name"]
            new_content = data["comment_content"]
            target      = Comment.objects.get(id = comment_id)

            if Comment.objects.get(id = comment_id).user.user_name == user_name:
                target.comment_content = new_content
                target.save()

                comments = Comment.objects.filter(work_id = work_id)
                comment_list = [ {
                    "id"              : comment.id,
                    "user_name"       : comment.user.user_name,
                    "comment_content" : comment.comment_content,
                    "created_at"      : comment.created_at
                } for comment in comments ]

                return JsonResponse({"MODIFY_SUCCESS": comment_list}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=400)

