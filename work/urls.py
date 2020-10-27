from django.urls import path
from work.views  import (
    TopCreatorsView,
    WallpaperMainFollowView,
    EditorPickWallpaperView,
    WallpaperCardListView,
    WallpaperdownloadcountView
)

urlpatterns = [
    path('/wallpaper/topcreators', TopCreatorsView.as_view()),
    path('/wallpaper/follow', WallpaperMainFollowView.as_view()),
    path('/wallpaper/editorpick', EditorPickWallpaperView.as_view()),
    path('/wallpaper/cardlist', WallpaperCardListView.as_view()),
    path('/wallpaper/download', WallpaperdownloadcountView.as_view()),
]
