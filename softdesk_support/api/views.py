from django.db import transaction
from django.http import Http404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Issue, Comment
from authentication.models import User

from .serializers import ProjectSerializer, IssueSerializer, \
    CommentSerializer
from authentication.serializers import UserSerializer

from authentication.permissions import IsAuthor, IsContributor


def get_object(pk, ressource_type):
    try:
        return ressource_type.objects.get(pk=pk)
    except ressource_type.DoesNotExist:
        raise Http404


class ProjectAPIView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get(self, request, pk=None, format=None):
        if pk is not None:
            project = get_object(pk, Project)
            serializer = ProjectSerializer(project)
        else:
            projects = Project.objects.all()
            serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # Serializing the data from the body of the request
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        project = get_object(pk, Project)
        serializer = ProjectSerializer(project, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = get_object(pk, Project)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])  # A voir avec post si ça ne fonctionne pas
    def add_collaborator(self, request, pk):
        # Définition d'une action accessible sur la méthode PATCH
        # Pour l'ajout d'un collaborateur à l'attribut du projet

        # detail car elle concerne un projet spécifique

        # Récupérer les données du collaborateur dans le corps de la requête
        # Ce qui spécifie un collaborateur (utilisateur) : nom d'utilisateur
        # Le nom d'utilisateur est unique
        collaborator_username = request.data['username']

        # Rechercher le collaborateur dans la base de données
        collaborator = User.objects.get(username=collaborator_username)

        # Rechercher le projet à partir de l'id spécifié dans le chemin
        project = Project.objects.get(pk=pk)
        # Ajouter le collaborateur au projet
        project.contributors.add(collaborator)
        # Enregistrer le projet
        project.save()

        return Response('New contributor added.')

    @action(detail=True,
            methods=['delete'])
    def delete_collaborator(self, request, pk):
        return Response('The contributor has been deleted from the project.')

class IssueAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get_queryset(self):
        return Issue.objects.all()

    def get(self, request, pk=None, format=None):
        if pk is not None:
            issue = get_object(pk, Issue)
            serializer = IssueSerializer(issue)
        else:
            issues = Issue.objects.all()
            serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        issue = get_object(pk, Issue)
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        print("Deleting ...")
        issue = get_object(pk, Issue)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentAPIView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get_queryset(self):
        return Comment.objects.all()

    def get(self, request, pk=None, format=None):
        if pk is not None:
            comment = get_object(pk, Comment)
            serializer = CommentSerializer(comment)
        else:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            print("OKKKK")
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        comment = get_object(pk, Comment)
        serializer = CommentSerializer(comment, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        comment = get_object(pk, Comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
