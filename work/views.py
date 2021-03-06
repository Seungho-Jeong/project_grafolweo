import random
import json

from django.http import JsonResponse
from django.views import View

from django.db.models import Count
from django.db import IntegrityError
from user.utils import login_decorator
from user.models import User, Follow
from work.models import (
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
        """
        작품 상세 페이지 조회
        :param work_id: 작품 ID(PK)
        :return:
            200: success
            400: exception error
            404: not found error
        """

        try:
            this_work = Work.objects.select_related("user").get(id=work_id)
            related_works = Work.objects.filter(user_id=this_work.user.id).exclude(id=work_id)

            # 조회수(Hits)
            this_work.views += 1
            this_work.save()

            detail = {
                "id": this_work.id,
                "title": this_work.title,
                "article": this_work.article,
                "creator": this_work.user.user_name,
                "creator_id": this_work.user.id,
                "creator_img": this_work.user.profile_image_url,
                "user_id": request.user.id if request.user else "GEUST",
                "user_name": request.user.user_name if request.user else "GEUST",
                "user_image": request.user.profile_image_url if request.user else "GEUST",
                "views": this_work.views,
                "created_at": this_work.created_at,
                "updated_at": this_work.updated_at,
                "image_url": [workimage.image_url for workimage in this_work.workimage_set.all()]
                             + [wallpaper.image_url for wallpaper in this_work.wallpaperimage_set.all()],
                "tag": [tag.name for tag in this_work.tag.all()],
                "follower_num": this_work.user.creator.all().count(),
                "following_num": this_work.user.follower.all().count(),
                "related_works": [{
                    "related_title": related_work.title,
                    "related_image_url": related_work.workimage_set.first().image_url
                } for related_work in related_works],
                "related_works_count": related_works.count()
            }
            return JsonResponse({"detail": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)


class CommentView(View):

    def get(self, request, work_id):
        """
        댓글 조회
        :param work_id: 작품 ID
        :return:
            200: success
            400: exception error
            404: not found error
        """

        try:
            if not Work.objects.filter(id=work_id).prefetch_related("comments").exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)

            comments_qs = Comment.objects.filter(work_id=work_id)

            comments_num = comments_qs.count()
            comments_lst = [{
                "comment_id": comment.id,
                "commenter_name": comment.user.user_name,
                "commenter_image": comment.user.profile_image_url,
                "comment_content": comment.comment_content,
                "comment_created_at": comment.created_at
            } for comment in comments_qs]
            return JsonResponse({"MESSAGE": "SUCCESS", "COUNT": comments_num, "LIST": comments_lst}, status=200)

        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)

    @login_decorator
    def post(self, request, work_id):
        """
        댓글 작성
        GET 메서드 생성
        :param request: comment_content
        :return:
            200: success
            400: key error, exception error
            404: not found error
        """

        try:
            data = json.loads(request.body)

            if not request.user:
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            if not Work.objects.filter(id=work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)

            Comment.objects.create(work_id=work_id,
                                   user_id=request.user.id,
                                   comment_content=data["comment_content"])

            return JsonResponse({"MESSAGE": "SUCCESS"}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "{}_IS_MISSING".format(e)}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)

    @login_decorator
    def delete(self, request, work_id, comment_id):
        """
        댓글 삭제
        :param work_id: 작품 ID
        :param comment_id: 삭제 대상 댓글 ID
        :return:
            200: success
            400: exception error
            401: authorization error
            404: not found error
        """

        try:
            if not request.user:
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            comment = Comment.objects.get(id=comment_id, work_id=work_id)
            comment.delete()

            return JsonResponse({"MESSAGE": "SUCCESS"}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=404)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)

    @login_decorator
    def patch(self, request, work_id, comment_id):
        """
        댓글 수정
        :param work_id: 작품 ID
        :parma comment_id: 수정 대상 댓글 ID
        :return:
            200: success
            401: authorization error
            404: not found error
        """

        try:
            data = json.loads(request.body)

            if Comment.objects.get(id=comment_id).user.id is not request.user.id:
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            target = Comment.objects.get(id=comment_id)
            target.comment_content = data["comment_content"]
            target.save()

            return JsonResponse({"MESSAGE": "SUCCESS"}, status=200)

        except Comment.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=404)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)


class CommentLikeView(View):
    @login_decorator
    def get(self, request, work_id, comment_id):
        """
        댓글 좋아요
        :param work_id: 작품 ID
        :param comment_id: 댓글 ID
        :return:
            200: create success, delete success
            400: exception error
            401: authorization error
            404: not found
        """

        try:
            user_id = request.user.id
            comment = CommentLike.objects.filter(comment_id=comment_id)

            if not Work.objects.filter(id=work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)

            if not Comment.objects.filter(id=comment_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_COMMENT"}, status=404)

            if not request.user:
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            if not comment.filter(user_id=user_id):
                CommentLike.objects.create(comment_id=comment_id, user_id=user_id)
                return JsonResponse({"MESSAGE": "SUCCESS", "LIKE": comment.count()})

            else:
                comment.filter(user_id=user_id)[0].delete()
                return JsonResponse({"MESSAGE": "SUCCESS", "LIKE": comment.count()})

        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)


class LikeView(View):

    def get(self, requset, work_id):
        """
        평가 조회
        :param work_id: 작품 ID
        :return:
            200: success
            404: not found error
        """

        try:
            if not Work.objects.filter(id=work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)

            like_kinds = LikeItKind.objects.all()

            like_num = LikeIt.objects.filter(work_id=work_id).count()
            like_lst = [{kind.name: LikeIt.objects.filter(work_id=work_id,
                                                          like_it_kind_id=kind).count()}
                        for kind in like_kinds]

            return JsonResponse({"MESSAGE": "SUCCESS", "TOT": like_num, "LIST": like_lst}, status=200)

        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)

    @login_decorator
    def post(self, request, work_id):
        """
        작품 평가
        :request:
            "like_it_kind_id": 1~3(JSON)
            1: 좋아요, 2: 감동받았어요, 3: 사고싶어요 (변경 가능)
        :return:
            200: change success, cancel success
            201: create success
            400: exception error
        """

        try:
            data = json.loads(request.body)

            if not Work.objects.filter(id=work_id).exists():
                return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)

            if not request.user:
                return JsonResponse({"MESSAGE": "UNAUTHORIZATION"}, status=401)

            user_id = request.user.id
            user_pick = data["like_it_kind_id"]
            user_picked = LikeIt.objects.filter(work_id=work_id, user_id=user_id)
            search_target = LikeIt.objects.filter(work_id=work_id)

            # 이미 내린 평가를 다시 클릭하는 경우(취소)
            if user_picked.filter(like_it_kind_id=user_pick).exists():
                user_picked.delete()

                picked_list = [hits for hits in search_target.values('like_it_kind_id').annotate(
                    like_count=Count('like_it_kind_id')).order_by("like_it_kind_id")]

                return JsonResponse({"MESSAGE": "SUCCESS", "PICKED_LIST": picked_list}, status=200)

            # 이미 평가를 내렸는데 다른 평가를 클릭하는 경우(변경)
            if user_picked:
                user_picked[0].like_it_kind_id = user_pick
                user_picked[0].save()

                picked_list = [hits for hits in search_target.values('like_it_kind_id').annotate(
                    like_count=Count('like_it_kind_id')).order_by("like_it_kind_id")]

                return JsonResponse({"MESSAGE": "SUCCESS", "PICKED_LIST": picked_list}, status=200)

            # 최초로 평가하는 경우(신규)
            else:
                LikeIt.objects.create(work_id=work_id, user_id=user_id, like_it_kind_id=user_pick)
                picked_list = [hits for hits in search_target.values('like_it_kind_id').annotate(
                    like_count=Count('like_it_kind_id')).order_by("like_it_kind_id")]

            return JsonResponse({"MESSAGE": "SUCCESS", "PICKED_LIST": picked_list}, status=201)

        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)


class WallpaperDetailView(View):
    def get(self, request, wallpaper_id):
        """
        배경화면 상세 페이지
        :param wallpaper_id: 배경화면 페이지 ID
        :return:
            200: success
            400: exception error
            404: not found error
        """

        try:
            this_wallpaper = WallpaperImage.objects.select_related("work", "themecolor").get(id=wallpaper_id)
            detail = {
                "id": this_wallpaper.id,
                "work_id": this_wallpaper.work.id,
                "title": this_wallpaper.work.title,
                "creator": this_wallpaper.work.user.user_name,
                "creator_img": this_wallpaper.work.user.profile_image_url,
                "views": this_wallpaper.work.views,
                "created_at": this_wallpaper.work.created_at,
                "image_url": this_wallpaper.image_url,
                "themecolor_id": this_wallpaper.themecolor_id,
                "downloadNum": this_wallpaper.download_count,
                "tag": [tag.name for tag in this_wallpaper.work.tag.all()],
            }
            return JsonResponse({"wallpaperDetails": detail}, status=200)

        except Work.DoesNotExist:
            return JsonResponse({"MESSAGE": "DOES_NOT_EXIST_PAGE"}, status=404)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERORR_IS_{}".format(e)}, status=400)


class TopCreatorsView(View):
    @login_decorator
    def get(self, request):
        CONST_LENGTH = 9
        creators = User.objects.all().prefetch_related('work_set')
        creatorlist = [{
            "id": creator.id,
            "user_name": creator.user_name,
            "profile_image_url": creator.profile_image_url,
            "followBtn": creator.creator.filter(follower_id=request.user.id).exists() if request.user else False,
            "likecount": sum([work.likeit_set.count() for work in creator.work_set.all()]),
        } for creator in creators]
        creatorlist = sorted(creatorlist, reverse=True, key=lambda x: x["likecount"])[:CONST_LENGTH]
        return JsonResponse({'topCreators': creatorlist}, status=200)


class FollowView(View):
    @login_decorator
    def post(self, request):
        if request.user:
            try:
                data = json.loads(request.body)
                user_id = request.user.id
                creator_id = data['creator_id']
                follow = Follow.objects.get(follower_id=user_id, creator_id=creator_id)
                follow.delete()
                data = {
                    "id": creator_id,
                    "followBtn": False
                }
                return JsonResponse({'data': data}, status=201)

            except Follow.DoesNotExist:
                try:
                    Follow.objects.create(follower_id=user_id, creator_id=creator_id)
                    data = {
                        "id": creator_id,
                        "followBtn": True
                    }
                    return JsonResponse({'data': data}, status=201)
                except IntegrityError:
                    return JsonResponse({'MESSAGE': "Error: unknown user"}, status=400)

            except KeyError as e:
                return JsonResponse({'MESSAGE': f"KeyError: {e}"}, status=400)
            except json.decoder.JSONDecodeError:
                return JsonResponse({'MESSAGE': "Error: json data error"}, status=400)

        return JsonResponse({'MESSAGE': "Need login"}, status=400)

    @login_decorator
    def get(self, request):
        creator_id = request.GET.get('creator_id')
        following = Follow.objects.filter(follower_id=request.user.id,
                                          creator_id=creator_id).exists() if request.user else False
        data = {
            "creator_id": creator_id,
            "followBtn": following
        }
        return JsonResponse({'data': data}, status=200)


class EditorPickWallpaperView(View):
    def get(self, request):
        CONST_LENGTH = 8
        tag_id = request.GET.get('tag')
        if tag_id:
            wallpaper_post = Work.objects.filter(tag__id=tag_id).select_related('user').prefetch_related(
                "wallpaperimage_set")
        else:
            taglistall = [{
                "id": tag.id,
                "name": tag.name
            } for tag in Tag.objects.all() if not tag.category_tag.exists()]
            taglist = random.sample(taglistall, 5)
            first_tag = taglist[0]["id"]
            wallpaper_post = Work.objects.filter(tag__id=first_tag).select_related('user').prefetch_related(
                "wallpaperimage_set")

        slides = [{
            "wallpaper_id": work.wallpaperimage_set.first().id,
            "subject": work.title,
            "wallpaperSrc": work.wallpaperimage_set.first().image_url,
            "name": work.user.user_name,
            "profileImgSrc": work.user.profile_image_url,
            "downloadNum": work.wallpaperimage_set.first().download_count
        } for work in wallpaper_post if work.wallpaperimage_set.exists()][:CONST_LENGTH]
        if tag_id:
            return JsonResponse({'editorsPickData': {"Slides": slides
                                                     }}, status=200)
        else:
            return JsonResponse({'editorsPickData': {
                "TagList": taglist,
                "Slides": slides
            }}, status=200)


class WallpaperCardListView(View):

    def get(self, request):

        def cardlist(works):
            if order == '최신순':
                works = works.order_by('-created_at')
            cardlist = [{
                "wallpaper_id": work.wallpaperimage_set.first().id,
                "subject": work.title,
                "wallpaperSrc": work.wallpaperimage_set.first().image_url,
                "name": work.user.user_name,
                "profileImgSrc": work.user.profile_image_url,
                "downloadNum": work.wallpaperimage_set.first().download_count,
                "views": work.views,
                "created_at": work.created_at
            } for work in works if work.wallpaperimage_set.exists()]
            if order == '인기순':
                cardlist = sorted(cardlist, reverse=True, key=lambda x: x["downloadNum"])
            return cardlist

        limit = int(request.GET.get('limit', '9'))
        offset = int(request.GET.get('offset', '0'))
        sort_name = request.GET.get('sort')
        order = request.GET.get('order', '최신순')
        id = request.GET.get('id')
        wallpaper_id = request.GET.get('wallpaper_id', '')
        filter = {
            '태그별': [Work.objects.filter(tag__id=id).select_related('user').prefetch_related("wallpaperimage_set"),
                    "discoverTagData"],
            '색상별': [Work.objects.filter(wallpaperimage__themecolor_id=id).select_related('user').prefetch_related(
                "wallpaperimage_set"), "discoverColorData"],
            '유형별': [Work.objects.filter(category__id=id).select_related('user').prefetch_related("wallpaperimage_set"),
                    "discoverTypeData"]
        }
        try:
            if not id and sort_name == "태그별":
                tag_list = [{
                    "id": tag.id,
                    "name": tag.name
                } for tag in Tag.objects.all() if not tag.category_tag.exists()][:10]
                taglist = [{"id": 0, "name": "전체"}] + tag_list
                works = Work.objects.all().select_related('user').prefetch_related("wallpaperimage_set")
                cardviewlist = cardlist(works)[offset:(offset + limit)]
                return JsonResponse({'discoverTagData': {
                    "tagList": taglist,
                    "cardViewList": cardviewlist
                }}, status=200)

            elif id == '0' and sort_name == "태그별":
                works = Work.objects.all().select_related('user').prefetch_related("wallpaperimage_set")
            elif id:
                works = filter[sort_name][0]
                if wallpaper_id:
                    works = works.exclude(wallpaperimage__id=wallpaper_id)
            else:
                return JsonResponse({'Error': "Need id"}, status=400)
            if works:
                cardviewlist = cardlist(works)[offset:(offset + limit)]
                return JsonResponse({filter[sort_name][1]: {"cardViewList": cardviewlist}}, status=200)
            else:
                return JsonResponse({'Error': "Invalid id"}, status=400)
        except KeyError:
            return JsonResponse({'Error': "Invalid sort_name"}, status=400)


class WallpaperdownloadcountView(View):

    def post(self, request):
        data = json.loads(request.body)
        WallpaperImage_id = data['wallpaper_id']
        try:
            wallpaper = WallpaperImage.objects.get(id=WallpaperImage_id)
            wallpaper.download_count += 1
            wallpaper.save()
            return JsonResponse({
                'MESSAGE': "Download Count Success",
                "image_url": wallpaper.image_url,
                "downloadNum": wallpaper.download_count
            }, status=200)
        except WallpaperImage.DoesNotExist:
            return JsonResponse({'Error': "Invalid wallpaper_id"}, status=400)


class WorksListView(View):

    @login_decorator
    def get(self, request):
        sort = request.GET.get('sort', '')
        limit = int(request.GET.get('limit', '9'))
        offset = int(request.GET.get('offset', '0'))
        category_id = request.GET.get('category_id', None)
        sort_order = [{
            '최신': '-created_at',
            '주목받는': '-views'
        }, {
            '발견': 'Likes',
            '데뷰': 'singup_time',
            '피드': 'id'
        }]

        filter_dict = {}

        if sort == '피드':
            filter_dict.update({'user__in': request.user.following.all()})
        if category_id:
            filter_dict.update({'category_id': category_id})

        works = Work.objects.filter(**filter_dict).select_related("user").prefetch_related("workimage_set",
                                                                                           "likeit_set", "comment_set")
        if sort in sort_order[0]:
            works = works.order_by(sort_order[0][sort])[offset:(offset + limit)]
        workslist = [{
            "id": work.id,
            "AuthorName": work.user.user_name,
            "AuthorProfile": work.user.profile_image_url,
            "PostName": work.title,
            "Img": work.workimage_set.first().image_url,
            "Likes": work.likeit_set.count(),
            "Comments": work.comment_set.count(),
            "Views": work.views,
            "singup_time": work.user.created_at
        } for work in works]
        if sort in sort_order[1]:
            workslist = sorted(workslist, reverse=True, key=lambda x: x[sort_order[1][sort]])[offset:(offset + limit)]
        return JsonResponse({'data': workslist}, status=200)


class CategoryListView(View):

    def get(self, request):
        categorylist = [{
            "categoryid": category.id,
            "categoryName": category.name,
            "categoryCount": category.work_set.count(),
            "backgroundColor": category.backgroundcolor,
            "image_url": category.image_url
        } for category in Category.objects.all().prefetch_related("work_set")]
        return JsonResponse({'data': categorylist}, status=200)


class CategoryTagView(View):

    def get(self, request):
        category_id = request.GET.get('category_id')
        categories_to_tags = CategoryToTag.objects.filter(category_id=category_id).select_related("tag", "category")
        if categories_to_tags:
            taglist = [{
                "id": category_to_tag.tag.id,
                "name": category_to_tag.tag.name
            } for category_to_tag in categories_to_tags]

            return JsonResponse(
                {'listBannerTags': taglist, "categoryImage": Category.objects.get(id=category_id).image_url},
                status=200)
        else:
            return JsonResponse({'MESSAGE': "wrong category"}, status=400)


class PopularCreatorView(View):

    def get(self, request):
        category_id = int(request.GET.get('category_id'))
        users = User.objects.all().prefetch_related("work_set", "user_to_follow")
        creatorlist = [{
            "id": user.id,
            "profileImgSrc": user.profile_image_url,
            "name": user.user_name,
            "desc": user.introduction,
            "follower": user.user_to_follow.count(),
            "like": sum([works.likeit_set.count() for works in user.work_set.all()]),
            "illust": user.work_set.count(),
            "imgPreviewSrc": [works.workimage_set.first().image_url for works in user.work_set.all()][:3],
            "category_like": sum(
                [works.likeit_set.count() for works in user.work_set.all() if works.category.id == category_id])
        } for user in users]
        creatorlist = sorted(creatorlist, reverse=True, key=lambda x: x["category_like"])[:16]
        return JsonResponse({'popularCreator': creatorlist}, status=200)
