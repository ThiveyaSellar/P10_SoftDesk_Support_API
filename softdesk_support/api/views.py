from django.db import transaction
from django.http import Http404
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Project, Issue, Comment
from authentication.models import User

from .serializers import ProjectSerializer, IssueSerializer, \
    CommentSerializer
from authentication.serializers import UserSerializer

from .permissions import IsAuthor, IsContributor


#@action(detail=True, methods=['patch']) # Action ne fonctionne pour les APIView mais pour les Viewset
@api_view(['PATCH'])
@permission_classes([IsAuthenticated & IsContributor | IsAuthor])
def add_collaborator(request, pk):
    # Définition d'une action accessible sur la méthode PATCH
    # Pour l'ajout d'un collaborateur à l'attribut du projet

    # detail car elle concerne un projet spécifique

    # Récupérer les données du collaborateur dans le corps de la requête
    # Ce qui spécifie un collaborateur (utilisateur) : nom d'utilisateur
    # Le nom d'utilisateur est unique

    if request.method == "PATCH":

        collaborator_username = request.data['username']

        # Rechercher le collaborateur dans la base de données
        collaborator = User.objects.get(username=collaborator_username)

        # Rechercher le projet à partir de l'id spécifié dans le chemin
        project = Project.objects.get(pk=pk)

        if project.author == request.user:      # Ajouter le collaborateur au projet
            project.contributors.add(collaborator)
            # Enregistrer le projet
            project.save()
            return Response({"message":'New contributor added.'})
        else:
            return Response({"message": "User doesn't have permission."})
    return Response({"message": "ERROR : Contributor hasn't been added to the project."})

@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsContributor | IsAuthor])
def delete_collaborator(request, pk):
    if request.method == 'DELETE':
        if 'username' not in request.data:
            return Response({"message":"Username is missing for deletion."})
        collaborator_username = request.data['username']
        collaborator = User.objects.get(username=collaborator_username)
        project = Project.objects.get(pk=pk)
        if project.author == request.user:
            project.contributors.remove(collaborator)
            project.save()
            return Response('The contributor has been deleted from the project.')
        else:
            return Response({"message": "User doesn't have permission."})
    return Response({"message": "ERROR : Contributor hasn't been deleted from the project."})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,IsContributor | IsAuthor])
def change_status(request,pk,pk2):
    if request.method == 'PATCH':
        # Récupérer le ticket en question grâce à l'id
        issue = Issue.objects.get(pk=pk2)
        # Récupérer le nouveau statut dans le corps de la requête
        if "status" not in request.data:
            return Response({
                'message': "Missing status field to change status."
            })
        if request.data["status"].upper() not in ['TO DO', 'IN PROGRESS','FINISHED']:
            return Response({
                'message':"Status must be 'TO DO', 'IN PROGRESS' OR 'FINISHED'"
            })
        # Changer le statut du ticket
        issue.status = request.data["status"]
        issue.save()
        return Response('The issue has a new status.')
    return Response({"message": "The status hasn't been changed."})

@api_view(['PATCH'])
@permission_classes([IsAuthenticated,IsContributor | IsAuthor])
def assign_contributor(request,pk,pk2):
    if request.method == 'PATCH':
        # Récupérer le ticket en question grâce à l'id
        issue = Issue.objects.get(pk=pk2)
        # Récupérer le nouveau statut dans le corps de la requête
        if "contributor" not in request.data:
            return Response({
                'message': "Missing contributor field with the username."
            })
        contributor_username = request.data["contributor"]
        try:
            contributor = User.objects.get(username=contributor_username)
        except User.DoesNotExist:
            return Response({"message": "username doesn't exist."})
        # Changer le statut du ticket
        issue.contributor = contributor
        issue.save()
        return Response('The issue has a new contributor.')
    return Response({"message": "The issue's contributor hasn't been changed."})

def get_object(pk, ressource_type):
    try:
        return ressource_type.objects.get(pk=pk)
    except ressource_type.DoesNotExist:
        raise Http404

class ProjectAPIView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated & IsContributor | IsAuthor]

    def get(self, request, pk=None, format=None):
        print("a")
        if pk is not None:
            print("b")
            project = get_object(pk, Project)
            self.check_object_permissions(request, project)
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
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get_queryset(self, pk):
        return Issue.objects.filter(project=pk)

    def get(self, request, pk, pk2=None, format=None):
        if pk2 is not None:
            issue = get_object(pk2, Issue)
            self.check_object_permissions(request, issue)
            serializer = IssueSerializer(issue)
        else:
            issues = Issue.objects.filter(project=pk)
            serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        # Compléter les données avant de sérialiser
        if "contributor" not in request.data:
            contributor = request.user.pk
        else:
            contributor_username = request.data["contributor"]
            try:
                contributor = User.objects.get(username=contributor_username).id
            except User.DoesNotExist:
                return Response({"message":"username doesn't exist."})
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
        print("icic")
        issue = get_object(pk2, Issue)
        self.check_object_permissions(request, issue)
        serializer = IssueSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        print("Deleting ...")
        issue = get_object(pk, Issue)
        self.check_object_permissions(request, issue)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CommentAPIView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsAdminUser]

    def get_queryset(self, pk):
        return Comment.objects.filter(issue=pk)

    def get(self, request, pk, pk2=None, format=None):
        if pk2 is not None:
            comment = get_object(pk2, Comment)
            self.check_object_permissions(request, comment)
            serializer = CommentSerializer(comment)
        else:
            comments = Comment.objects.filter(issue=pk)
            serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        # Compléter les données avant de sérialiser
        try:
            issue = Issue.objects.get(pk=pk)
            project = issue.project.id
        except Issue.DoesNotExist:
            raise Http404
        data = request.data.copy()
        data.update({
            'project': project,
            'author': request.user.pk,
            'issue': pk
        })
        serializer = CommentSerializer(data=data)
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
        self.check_object_permissions(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserTicketsAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get_queryset(self, pk, pk2):
        # Récupérer tous les tickets d'un contributeur pour un projet
        return Issue.objects.filter(contributor=pk, project=pk2)

    def get(self, request, pk, pk2, format=None):
        issues = Issue.objects.filter(contributor=pk, project=pk2)
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)