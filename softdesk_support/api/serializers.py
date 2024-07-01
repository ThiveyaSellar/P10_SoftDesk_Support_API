from rest_framework.serializers import ModelSerializer
from api.models import Project, Issue, Comment


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

    class Meta:
        model = Issue
        fields = [
            'created_time',
            'author',
            'contributor',
            'project',
            'name',
            'description',
            'status',
            'priority',
            'tag'
        ]


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'created_time',
            'author',
            'description',
            'project',
            'issue'
        ]
