from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from .permissions import IsOwner

from .models import User
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import SignUpSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserViewSet(ModelViewSet):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsOwner | IsAdminUser]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.none()

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"detail": "User not found."},
                            status=status.HTTP_404_NOT_FOUND)


class SignUpView(ViewSet):

    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        # Sérialiser les données récupérées dans le corps de la requête
        serializer = SignUpSerializer(data=request.data)
        # Validation des données lors de la deserialization
        # Pour vérifier que les données soient conformes aux attentes de l'app
        # serializer.errors pour afficher les erreurs
        if 'can_be_contacted' not in request.data or \
                'can_data_be_shared'not in request.data:
            return Response(
                {
                    'can_be_contacted': 'This field is required.',
                    'can_data_be_shared': 'This field is required.'
                },
                status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    def post(self, request):
        if 'username' not in request.data or 'password' not in request.data:
            return Response(
                {'message': 'Missing credentials.'},
                status.HTTP_400_BAD_REQUEST
            )
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'message': 'Credentials are invalid.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        login(request, user)
        tokens = get_tokens_for_user(request.user)
        return Response(
            {'message': 'Successfully logged', **tokens},
            status=status.HTTP_200_OK
        )
