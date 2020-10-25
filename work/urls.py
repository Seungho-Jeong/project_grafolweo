from django.urls import path
from work.views  import (
    TopCreatorsView,
    WallpaperMainFollowView,
)

urlpatterns = [
    path('/wallpaper/topcreators', TopCreatorsView.as_view()),
    path('/wallpaper/follow', WallpaperMainFollowView.as_view()),
]