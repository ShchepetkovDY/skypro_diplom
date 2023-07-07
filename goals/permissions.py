from rest_framework import permissions

from goals.models import BoardParticipant


class BoardPermissions(permissions.BasePermission):
    """
    В коде выше мы:
        - Определили метод `has_object_permission`, который должен вернуть `True`,
          если доступ у пользователя есть, и `False` — если нет.
        - Если пользователь не авторизован, всегда возвращаем False.
        - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
          то тогда просто проверяем, что существует участник у данной доски.
        - Если метод не входит (это значит, что мы пытаемся изменить или удалить доску), то обязательно проверяем,
          что наш текущий пользователь является создателем доски.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner).exists()


class GoalCategoryPermissions(permissions.BasePermission):
    """
    В коде выше мы:
        - Определили метод `has_object_permission`, который должен вернуть `True`,
          если доступ у пользователя есть, и `False` — если нет.
        - Если пользователь не авторизован, всегда возвращаем False.
        - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
          то тогда просто проверяем, что существует участник у данной категории.
        - Если метод не входит (это значит, что мы пытаемся изменить или удалить категорию), то обязательно проверяем,
          что наш текущий пользователь является создателем категории.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj.board).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj.board,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists()


class GoalPermissions(permissions.BasePermission):
    """
    В коде выше мы:
        - Определили метод `has_object_permission`, который должен вернуть `True`,
          если доступ у пользователя есть, и `False` — если нет.
        - Если пользователь не авторизован, всегда возвращаем False.
        - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
          то тогда просто проверяем, что существует участник у данной цели.
        - Если метод не входит (это значит, что мы пытаемся изменить или удалить цель), то обязательно проверяем,
          что наш текущий пользователь является создателем цели.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=obj.category.board).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj.category.board,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ).exists()


class CommentPermissions(permissions.BasePermission):
    """
    В коде выше мы:
        - Определили метод `has_object_permission`, который должен вернуть `True`,
          если доступ у пользователя есть, и `False` — если нет.
        - Если пользователь не авторизован, всегда возвращаем False.
        - Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
          то тогда просто проверяем, что существует участник у данного комментария.
        - Если метод не входит (это значит, что мы пытаемся изменить или удалить комментарий), то обязательно проверяем,
          что наш текущий пользователь является создателем комментария.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
