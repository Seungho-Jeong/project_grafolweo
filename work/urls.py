from django.urls import path
from work.views  import (
    WorksListView,
    MainCategoryView,
    CategoryTagView,
    PopularCreatorView
)

urlpatterns = [
    path('/main/list/<str:sort>/<int:page>', WorksListView.as_view()),
    path('/main/category', MainCategoryView.as_view()),
    path('/category/<str:category>', CategoryTagView.as_view()),
    path('/category/popular_creator/<str:category>', PopularCreatorView.as_view()),
]