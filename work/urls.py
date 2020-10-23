from django.urls    import path

from .views         import WorkShowView

urlpatterns = [
    path('', WorkShowView.as_view()),
]
