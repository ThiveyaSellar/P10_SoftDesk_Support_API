from django.db import transaction
from django.http import Http404
from rest_framework.decorators import action, api_view
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


#@action(detail=True, methods=['patch']) # Action ne parait pas fonctionner pour les APIView mais pour les Viewset
@api_view(['PATCH'])
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
        # Ajouter le collaborateur au projet
        project.contributors.add(collaborator)
        # Enregistrer le projet
        project.save()

        return Response({"message":'New contributor added.'})
    return Response({"message": "ERROR : Contributor hasn't been added to the project."})

@api_view(['DELETE'])
def delete_collaborator(request, pk):
    if request.method == 'DELETE':
        if 'username' not in request.data:
            return Response({"message":"Username is missing for deletion."})
        collaborator_username = request.data['username']
        collaborator = User.objects.get(username=collaborator_username)
        project = Project.objects.get(pk=pk)
        project.contributors.remove(collaborator)
        project.save()
        return Response('The contributor has been deleted from the project.')
    return Response({"message": "ERROR : Contributor hasn't been deleted from the project."})

@api_view(['PATCH'])
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
    """permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]"""
    permission_classes = [IsAuthenticated,
                          IsAuthor]
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
        print("----------------ICI------------------------")
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


class IssueAPIView(APIView):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated,
                          IsAuthor | IsContributor | IsAdminUser]

    def get_queryset(self, pk):
        return Issue.objects.filter(project=pk)

    def get(self, request, pk, pk2=None, format=None):
        if pk2 is not None:
            issue = get_object(pk2, Issue)
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

    def patch(self, request, pk2, format=None):
        issue = get_object(pk2, Issue)
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

    def get_queryset(self, pk):
        return Comment.objects.filter(issue=pk)

    def get(self, request, pk, pk2=None, format=None):
        if pk2 is not None:
            comment = get_object(pk2, Comment)
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