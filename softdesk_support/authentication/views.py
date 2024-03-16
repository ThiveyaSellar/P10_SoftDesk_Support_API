from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from authentication.permissions import IsOwnerOrReadOnly

from authentication.models import User
from authentication.serializers import UserSerializer

class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return User.objects.all()