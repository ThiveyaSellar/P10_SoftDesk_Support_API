from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Issue, Comment
from authentication.models import User

from .serializers import ProjectSerializer, IssueSerializer, \
    CommentSerializer

from .permissions import IsAuthor, IsContributor
from authentication.permissions import IsOwner


@api_view(['PATCH'])
@permission_classes([IsAuthenticated & IsContributor | IsAuthor | IsAdminUser])
def add_collaborator(request, pk):
    # Définition d'une action accessible sur la méthode PATCH
    # Pour l'ajout d'un collaborateur à l'attribut du projet

    # detail car elle concerne un projet spécifique

    # Récupérer les données du collaborateur dans le corps de la requête
    # Ce qui spécifie un collaborateur (utilisateur) : nom d'utilisateur
    # Le nom d'utilisateur est unique

    if request.method == "PATCH":
        print("ok")
        collaborator_username = request.data['username']

        # Rechercher le collaborateur dans la base de données
        collaborator = User.objects.get(username=collaborator_username)

        # Rechercher le projet à partir de l'id spécifié dans le chemin
        project = Project.objects.get(pk=pk)

        if project.author == request.user or request.user.is_superuser:
            project.contributors.add(collaborator)
            # Enregistrer le projet
            project.save()
            return Response({"message": 'New contributor added.'})
        else:
            return Response({"message": "User doesn't have permission."})
    return Response({
        "message": "ERROR : Contributor hasn't been added to the project."
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated & IsContributor | IsAuthor | IsAdminUser])
def delete_collaborator(request, pk):
    if request.method == 'DELETE':
        if 'username' not in request.data:
            return Response({"message": "Username is missing for deletion."})
        collaborator_username = request.data['username']
        collaborator = User.objects.get(username=collaborator_username)
        project = Project.objects.get(pk=pk)
        if project.author == request.user or request.user.is_superuser:
            project.contributors.remove(collaborator)
            project.save()
            return Response({
                "message": "The contributor has been deleted from the project."
            })
        else:
            return Response({
                "message": "User doesn't have permission."
            })
    return Response({
        "message": "ERROR : Contributor hasn't been deleted from the project."
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated & IsContributor | IsAuthor | IsAdminUser])
def change_status(request, pk, pk2):
    if request.method == 'PATCH':
        # Récupérer le ticket en question grâce à l'id
        issue = Issue.objects.get(pk=pk2)

        if issue.author != request.user and not request.user.is_superuser:
            return Response({
                'message': 'You don\'t have permissions.'
            })
        # Récupérer le nouveau statut dans le corps de la requête
        if "status" not in request.data:
            return Response({
                'message': "Missing status field to change status."
            })
        data_status = request.data["status"].upper()
        if data_status not in ['TO DO', 'IN PROGRESS', 'FINISHED']:
            return Response({
                'message': "Status must be 'TO DO', 'IN PROGRESS', 'FINISHED'"
            })
        # Changer le statut du ticket
        issue.status = request.data["status"]
        issue.save()
        return Response('The issue has a new status.')
    return Response({"message": "The status hasn't been changed."})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated & IsContributor | IsAuthor | IsAdminUser])
def assign_contributor(request, pk, pk2):
    if request.method == 'PATCH':
        # Récupérer le ticket en question grâce à l'id
        issue = Issue.objects.get(pk=pk2)
        # Récupérer le nouveau statut dans le corps de la requête
        if issue.author != request.user and not request.user.is_superuser:
            return Response({
                'message': 'You don\'t have permissions.'
            })

        if "contributor" not in request.data:
            return Response({
                'message': "Missing contributor field with the username."
            })
        contributor_username = request.data["contributor"]
        try:
            contributor = User.objects.get(username=contributor_username)
        except User.DoesNotExist:
            return Response({"message": "username doesn't exist."})
        if contributor not in issue.project.contributors.all():
            return Response({
                'message': 'User is not part of the project.'
            })
        # Changer le statut du ticket
        issue.contributor = contributor
        issue.save()
        serializer = IssueSerializer(issue)
        return Response(serializer.data)
    return Response({
        "message": "The issue's contributor hasn't been changed."
    })


def get_object(pk, ressource_type):
    try:
        return ressource_type.objects.get(pk=pk)
    except ressource_type.DoesNotExist:
        raise Http404


class ProjectAPIView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated & IsAuthor | IsContributor | IsAdminUser]

    def get(self, request, pk=None, format=None):
        if pk is not None:
            project = get_object(pk, Project)
            self.check_object_permissions(request, project)
            if (
                    request.user in project.contributors.all() or
                    project.author == request.user or
                    request.user.is_superuser
            ):
                serializer = ProjectSerializer(project)
            else:
                return Response(
                    {"detail": "You don't have permissions."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            user = request.user
            projects = Project.objects.filter(
                Q(author=user) | Q(contributors=user)
            )
            serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = request.data.copy()
        data.update({
            'author': request.user.pk,
            'contributors': request.user.pk
        })
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        project = get_object(pk, Project)
        self.check_object_permissions(request, project)
        serializer = ProjectSerializer(project, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = get_object(pk, Project)
        self.check_object_permissions(request, project)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated & IsContributor | IsAuthor | IsAdminUser]

    def get_queryset(self, pk):
        return Issue.objects.filter(project=pk)

    def get(self, request, pk, pk2=None, format=None):
        project = get_object(pk, Project)
        if pk2 is not None:
            # Récupérer le ticket qui a pour projet le projet récupéré
            issue = get_object_or_404(Issue, pk=pk2, project=project)
            self.check_object_permissions(request, issue)
            serializer = IssueSerializer(issue)
        else:
            if (
                    request.user not in project.contributors.all() and
                    not request.user.is_superuser
            ):
                return Response({
                    'message': 'You are not a collaborator of this project.'
                })
            issues = Issue.objects.filter(project=pk)
            serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request, pk, pk2=None, format=None):
        # Compléter les données avant de sérialiser
        project = get_object(pk, Project)
        self.check_object_permissions(request, project)
        if "contributor" not in request.data:
            contributor = request.user.pk
            print(contributor)
        else:
            contributor_username = request.data["contributor"]
            try:
                contributor = User.objects.get(username=contributor_username).id
            except User.DoesNotExist:
                return Response({"message": "username doesn't exist."})
        data = request.data.copy()
        data.update({
            'project': pk,
            'author': request.user.pk,
            'contributor': contributor
        })
        serializer = IssueSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, pk2, format=None):
        issue = get_object(pk2, Issue)
        self.check_object_permissions(request, issue)
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, pk2, format=None):
        print("Deleting ...")
        issue = get_object(pk2, Issue)
        self.check_object_permissions(request, issue)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentAPIView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated & IsContributor | IsAuthor | IsAdminUser]

    def get_queryset(self, pk):
        # pk correspond à l'id de l'issue
        return Comment.objects.filter(issue=pk)

    def get(self, request, pk, pk2=None, format=None):
        issue = get_object(pk, Issue)
        project = issue.project
        self.check_object_permissions(request, project)
        if pk2 is not None:
            # Récupérer le ticket avec pk
            comment = get_object(pk2, Comment)
            self.check_object_permissions(request, comment)
            serializer = CommentSerializer(comment)
        else:
            # Affiche tous les commentaires d'un ticket
            comments = Comment.objects.filter(issue=pk)
            serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        # Compléter les données avant de sérialiser
        issue = get_object(pk, Issue)
        project = issue.project
        self.check_object_permissions(request, project)
        data = request.data.copy()
        data.update({
            'project': project.id,
            'author': request.user.pk,
            'issue': pk
        })
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, pk2=None, format=None):
        comment = get_object(pk2, Comment)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, pk2, format=None):
        get_object(pk, Issue)
        comment = get_object(pk2, Comment)
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserTicketsAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated &
                          IsOwner | IsAdminUser]

    def get_queryset(self, pk, pk2):
        # Récupérer tous les tickets d'un contributeur pour un projet
        return Issue.objects.filter(contributor=pk, project=pk2)

    def get(self, request, pk, pk2, format=None):
        issues = Issue.objects.filter(contributor=pk, project=pk2)
        user = get_object(pk, User)
        self.check_object_permissions(request, user)
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)
