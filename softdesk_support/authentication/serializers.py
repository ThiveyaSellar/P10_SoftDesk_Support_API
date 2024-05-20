from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CharField

from .models import User
from api.serializers import ProjectSerializer

class UserSerializer(ModelSerializer):

    # projects = ProjectSerializer(many=True)
    projects = ProjectSerializer(many=True, required=False, allow_null=True)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'created_time',
            'first_name',
            'last_name',
            'age',
            'can_be_contacted',
            'can_data_be_shared',
            'projects'
        ]

class SignUpSerializer(ModelSerializer):

    password2 = CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]

    def create(self, data):
        """
        Sign up the new user
        """
        # Check if passwords match
        password = self.data['password']
        password2 = self.data['password2']

        if password != password2:
            raise serializers.ValidationError(
                {
                    'name':'Passwords don\'t match'
                }
            )

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {
                    'email': 'An account with this email already exists.'
                }
            )

        user = User.objects.create_user(
            email=data['email'],
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=password,
            age=data['age'],
            can_data_be_shared=data['can_data_be_shared'],
            can_be_contacted=data['can_be_contacted']
        )
        return user
