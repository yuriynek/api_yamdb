from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'api'

API_VERSION = 'v1'

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='categories api endpoint')
router.register('genres', views.CategoryViewSet, basename='genres api endpoint')
router.register('titles', views.TitleViewSet, basename='titles api endpoint')
router.register(r'titles/(?P<post_id>\d+)/reviews',
                views.ReviewViewSet,
                basename='title reviews api endpoint')
router.register(r'titles/(?P<post_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                views.CommentViewSet,
                basename='reviews comments api endpoint')

urlpatterns = [
    path(f'{API_VERSION}/', include(router.urls)),
]
