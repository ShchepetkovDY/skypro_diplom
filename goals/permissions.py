# from rest_framework import permissions
# from rest_framework.generics import GenericAPIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.request import Request
#
# from goals.models import Goal
#
#
# class GoalCategoryPermissions(permissions.BasePermission):
#     """
#     В коде выше мы:
#         - Определили метод `has_object_permission`, который должен вернуть `True`,
#           если доступ у пользователя есть, и `False` — если нет.
#         - Если пользователь не авторизован, всегда возвращаем False.
#         - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
#           то тогда просто проверяем, что существует участник у данной категории.
#         - Если метод не входит (это значит, что мы пытаемся изменить или удалить категорию), то обязательно проверяем,
#           что наш текущий пользователь является создателем категории.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         if not request.user.is_authenticated:
#             return False
#
#
# class GoalPermissions(IsAuthenticated):
#     def has_object_permission(self, request: Request, view: GenericAPIView, obj: Goal) -> bool:
#         return obj.user == request.user
#
#
# class CommentPermissions(permissions.BasePermission):
#     """
#     В коде выше мы:
#         - Определили метод `has_object_permission`, который должен вернуть `True`,
#           если доступ у пользователя есть, и `False` — если нет.
#         - Если пользователь не авторизован, всегда возвращаем False.
#         - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
#           то тогда просто проверяем, что существует участник у данного комментария.
#         - Если метод не входит (это значит, что мы пытаемся изменить или удалить комментарий), то обязательно проверяем,
#           что наш текущий пользователь является создателем комментария.
#     """
#     def has_object_permission(self, request, view, obj):
#         if not request.user.is_authenticated:
#             return False
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.user == request.user