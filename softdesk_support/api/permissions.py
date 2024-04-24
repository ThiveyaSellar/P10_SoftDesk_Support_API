from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthor(BasePermission):
    # On peut implémenter has_permission et/ou has_object_permission
    # Pour que has_object_permission soit appelé has_permission doit réussir
    # Les vues génériques vérifient les autorisations au niveau des objets
    # Pour les autorisations personnalisées, vérifier par soi même avec
    # self.check_object_permissions(request, obj) une fois l'instance récupérée

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsContributor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user in obj.contributors.all()
        print("nop")
        return False


