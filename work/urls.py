from django.urls import path
from work.views  import (
    TopCreatorsView,
    FollowView,
    EditorPickWallpaperView,
    WallpaperCardListView,
    WallpaperdownloadcountView,
    WorksListView,
    CategoryListView,
    CategoryTagView,
    PopularCreatorView,
    WorkDetailView,
    CommentView,
    LikeView,
    CommentLikeView,
    WallpaperDetailView
)

urlpatterns = [
    path('/wallpaper/topcreators', TopCreatorsView.as_view()),
    path('/follow', FollowView.as_view()),
    path('/wallpaper/editorpick', EditorPickWallpaperView.as_view()),
    path('/wallpaper/cardlist', WallpaperCardListView.as_view()),
    path('/wallpaper/download', WallpaperdownloadcountView.as_view()),
    path('/list', WorksListView.as_view()),
    path('/category', CategoryListView.as_view()),
    path('/tag', CategoryTagView.as_view()),
    path('/popular_creator', PopularCreatorView.as_view()),
    path('/<int:work_id>', WorkDetailView.as_view()),
    path('/<int:work_id>/comments', CommentView.as_view()),
    path('/<int:work_id>/comment/<int:comment_id>', CommentView.as_view()),
    path('/<int:work_id>/comment/<int:comment_id>/like', CommentLikeView.as_view()),
    path('/<int:work_id>/likeit', LikeView.as_view()),
    path('/wallpaper/<int:wallpaper_id>', WallpaperDetailView.as_view())
]
