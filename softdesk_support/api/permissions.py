from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthor(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author` attribute.
    IsOwnerOrReadOnly dans la doc DRF
    """

    """def has_permission(self, request, view):
        # Les SAFE_METHODS : GET, HEAD or OPTIONS requests.
        #if request.method in SAFE_METHODS:
         #   return True
        return False
        # Instance must have an attribute named `owner`.
        # Checking if the object is the user himself or
        # checking if the object has a author attribute that is the user who makes the request
        #return obj == request.user or obj.author == request.user"""

    """def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True"""

    def has_object_permission(self, request, view, obj):
        print("--------has_object_permission---------")
        print("request.user",request.user)
        print("obj.author",obj.author)
        if obj.author == request.user:
            return False
        return False

class IsContributor(BasePermission):
    """
    Permissions to owner and contributor to get and edit it
    """

    def has_object_permission(self, request, view, obj):
        is_owner = obj == request.user or obj.author == request.user
        is_collaborator = request.user in obj.contributors.all()

        return is_owner or is_collaborator
