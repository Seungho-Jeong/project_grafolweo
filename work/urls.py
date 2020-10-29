from django.urls    import path

from .views         import WorkDetailView, CommentView, LikeView, CommentLikeView

urlpatterns = [
    path('/<int:work_id>', WorkDetailView.as_view()),
    path('/<int:work_id>/comments', CommentView.as_view()),
    path('/<int:work_id>/comment/<int:comment_id>', CommentView.as_view()),
    path('/<int:work_id>/comment/<int:comment_id>/like',CommentLikeView.as_view()),
    path('/<int:work_id>/likeit', LikeView.as_view()),
]
