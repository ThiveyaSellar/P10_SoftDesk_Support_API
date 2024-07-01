"""
URL configuration for softdesk_support project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView

from authentication.views import UserViewSet
from api.views import ProjectAPIView, IssueAPIView, CommentAPIView, \
    add_collaborator, delete_collaborator, change_status, assign_contributor

# Utilisation d'un router pour la ressource User défini avec un ModelViewSet
from authentication.views import SignUpView, LoginView
from api.views import UserTicketsAPIView

router = routers.SimpleRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('api/sign-up/', SignUpView.as_view({'post': 'create'})),
    path('api/login/', LoginView.as_view()),
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(
        'api/token/refresh',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path('api/projects', ProjectAPIView.as_view()),
    path('api/projects/<int:pk>/', ProjectAPIView.as_view()),
    path('api/projects/<int:pk>/add_collaborator', add_collaborator),
    path('api/projects/<int:pk>/delete_collaborator', delete_collaborator),

    path('api/projects/<int:pk>/issues', IssueAPIView.as_view()),
    path('api/projects/<int:pk>/issues/<int:pk2>/', IssueAPIView.as_view()),
    path(
        'api/projects/<int:pk>/issues/<int:pk2>/change_status',
        change_status
    ),
    path(
        'api/projects/<int:pk>/issues/<int:pk2>/assign_contributor',
        assign_contributor
    ),

    path('api/issues/<int:pk>/comments', CommentAPIView.as_view()),
    path('api/issues/<int:pk>/comments/<int:pk2>/', CommentAPIView.as_view()),

    path(
        'api/users/<int:pk>/projects/<int:pk2>/tickets/',
        UserTicketsAPIView.as_view()
    )
]
