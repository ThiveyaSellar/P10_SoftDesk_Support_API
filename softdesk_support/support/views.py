from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from support.models import User, Project, Issue, Comment
from support.serializers import UserSerializer, ProjectSerializer, \
    IssueSerializer, CommentSerializer

class UserAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
