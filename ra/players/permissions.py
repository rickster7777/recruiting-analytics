from django.contrib.auth.models import Group
from rest_framework import permissions

from ra_user.models import User


class FixFitfinderSavedSearchPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        user_group = User.objects.filter(
            username=request.user).values_list('groups__name', flat=True)

        if request.user.is_staff or 'admin' in user_group:
            return True

        elif 'coach' in user_group and request.method in ['GET', 'POST']:
            return True
        else:
            return True

    def has_object_permission(self, request, view, obj):

        user_group = User.objects.filter(
            username=request.user
        ).values_list('groups__name', flat=True)

        if ('admin' in user_group or request.user.is_staff):
            return True

        elif ('coach' in user_group and request.method in ['PUT', 'PATCH']):
            return request.user.username == obj.search_by.username

        # elif ('brand_admin' or 'university_admin' in user_group) and \
        #         request.method in ['PUT', 'PATCH']:
            # return request.user.username == obj.username
        elif ('coach' in user_group and request.method in ['GET', ]):
            return True
        else:
            return False


class FixCommentsPermission(permissions.BasePermission):
    """
    Comments Permissions for Coach and Admin can only access the request data
    UC Admin can access CRUD Operations.
    """

    def has_permission(self, request, view):
        user_group = User.objects.filter(
            username=request.user
        ).values_list('groups__name', flat=True)

        if request.user.is_staff or 'admin' in user_group:
            return True

        elif 'coach' in user_group and request.method in ['GET', 'POST']:
            return True
        else:
            return True

    def has_object_permission(self, request, view, obj):

        user_group = User.objects.filter(
            username=request.user
        ).values_list('groups__name', flat=True)

        if ('admin' in user_group or request.user.is_staff):
            return True

        elif ('coach' in user_group and request.method in ['PUT', 'PATCH', 'DELETE']):
            return request.user.username == obj.commented_by.username

        # elif ('brand_admin' or 'university_admin' in user_group) and \
        #         request.method in ['PUT', 'PATCH']:
            # return request.user.username == obj.username
        elif ('coach' in user_group and request.method in ['GET', ]):
            return True
        else:
            return False
