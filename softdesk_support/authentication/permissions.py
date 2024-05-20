from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `author` attribute.
    IsOwnerOrReadOnly dans la doc DRF
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            print("aa")
            return True

        print("bb")
        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        print("a")
        if request.method in SAFE_METHODS:
            print("b")
            return True
        print("c")
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user