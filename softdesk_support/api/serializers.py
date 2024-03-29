from rest_framework.serializers import ModelSerializer

from support.models import User, Project, Issue, Comment

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'created_time',
            'age',
            'can_be_contacted',
            'can_data_be_shared'
        ]

class ProjectSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = [
            'created_time',
            'author',
            'contributors',
            'name',
            'description',
            'type'
        ]

class IssueSerializer(ModelSerializer):
    pass

class CommentSerializer(ModelSerializer):
    pass