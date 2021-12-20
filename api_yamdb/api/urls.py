from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views


app_name = 'api'

API_VERSION = 'v1'

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='categories api endpoint')
router.register('genres', views.GenreViewSet, basename='genres api endpoint')
router.register('titles', views.TitleViewSet, basename='titles api endpoint')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                views.ReviewViewSet,
                basename='title reviews api endpoint')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
                views.CommentViewSet,
                basename='reviews comments api endpoint')
router.register('auth/signup', views.UserCreateThroughEmailViewSet,
                basename='sign up api endpoint')
router.register('users', views.UserViewSet,
                basename='users api endpoint')


urlpatterns = [
    path(f'{API_VERSION}/users/me/', views.user_own_view, name='user_own_info'),
    path(f'{API_VERSION}/', include(router.urls)),
    path(f'{API_VERSION}/auth/token/', views.get_tokens_for_user, name='token_obtain_pair'),
]
