from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from support.models import User, Project, Issue, Comment
from support.serializers import UserSerializer, ProjectSerializer, \
    IssueSerializer, CommentSerializer

class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.all()


class ProjectViewSet(ModelViewSet):

    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()

