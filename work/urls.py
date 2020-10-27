
from django.urls    import path

from .views         import WorkDetailView, CommentView

urlpatterns = [
    path('/<int:work_id>', WorkDetailView.as_view()),
    path('/<int:work_id>/comments', CommentView.as_view()),
    path('/<int:work_id>/comment/<int:comment_id>', CommentView.as_view()),
]

