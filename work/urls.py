from django.urls import path
from work.views  import (
    WorksListView,
    CategoryListView,
    CategoryTagView,
    PopularCreatorView
)

urlpatterns = [
    path('/list', WorksListView.as_view()),
    path('/category', CategoryListView.as_view()),
    path('/tag/<int:category_id>', CategoryTagView.as_view()),
    path('/popular_creator', PopularCreatorView.as_view()),
]