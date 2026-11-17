from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_admin_role()
        )

class IsReviewerOrAdmin(permissions.BasePermission):
    """
    Allows access to reviewers and admins (can upload, edit, correct fields).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_reviewer_role()
        )

class IsViewerOrAboveReadOnly(permissions.BasePermission):
    """
    Viewers can read; Reviewers and Admins can write.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_reviewer_role()

