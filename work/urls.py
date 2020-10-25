from django.urls import path
from work.views  import (
    TopCreatorsView,
    WallpaperMainFollowView,
    EditorPickWallpaperView,
)
    # EditorPickWallpapertagView

urlpatterns = [
    path('/wallpaper/topcreators', TopCreatorsView.as_view()),
    path('/wallpaper/follow', WallpaperMainFollowView.as_view()),
    path('/wallpaper/editorpick', EditorPickWallpaperView.as_view()),
]
    # path('/wallpaper/editorpick/<int:tageid>', EditorPickWallpapertagView.as_view()),