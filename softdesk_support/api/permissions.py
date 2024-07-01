from rest_framework.permissions import BasePermission
from .models import Issue, Comment


class IsAuthor(BasePermission):
    # Pour que has_object_permission soit appelé has_permission doit réussir
    # Les vues génériques vérifient les autorisations au niveau des objets
    # Pour les autorisations personnalisées, vérifier par soi-même avec
    # self.check_object_permissions(request, obj) une fois l'instance récupérée
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsContributor(BasePermission):

    def has_object_permission(self, request, view, obj):
        # Collaborateur a la permission de modifier ou de supprimer
        if request.method == 'DELETE' or request.method == 'PATCH':
            return False
        # Permission d'afficher s'il est collaborateur du projet
        # Est-ce qu'il est collaborateur du projet ?
        # Est-ce que l'issue appartient à un projet où il est collaborateur ?
        if request.method == 'GET':
            if isinstance(obj, Issue):
                return request.user in obj.project.contributors.all()
            if isinstance(obj, Comment):
                return request.user in obj.issue.project.contributors.all()
        return request.user in obj.contributors.all()
