from django.urls import path
from work.views  import (
    WorksListView,
    CategoryTagView,
    PopularCreatorView
)

urlpatterns = [
    path('/list/<str:sort>/<int:page>', WorksListView.as_view()),
    path('/category/<str:category>', CategoryTagView.as_view()),
    path('/category/list/popular_creator', PopularCreatorView.as_view()),
]