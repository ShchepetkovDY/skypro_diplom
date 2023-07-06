from rest_framework import permissions
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment
from goals.serializers import (
    GoalCreateSerializer,
    GoalCategorySerializer,
    GoalSerializer,
    CommentCreateSerializer,
    CommentSerializer,
    GoalCategoryCreateSerializer,
)


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived
        instance.save()
        return instance


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GoalDateFilter
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority"]
    ordering = ["priority", "due_date"]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)


class CommentCreateView(CreateAPIView):
    model = GoalComment
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)


class CommentListView(ListAPIView):
    model = GoalComment
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["goal"]
    ordering = "-id"

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)


# from django.db import transaction
# from django.db.models import QuerySet
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import permissions, filters
# from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
# from rest_framework.pagination import LimitOffsetPagination
#
# from goals.filters import GoalDateFilter
# from goals.models import GoalCategory, Goal, GoalComment
# from goals.permissions import GoalCategoryPermissions, GoalPermissions, CommentPermissions
# from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalSerializer, \
#     GoalCreateSerializer, CommentCreateSerializer, CommentSerializer
#
#
# class GoalCategoryCreateView(CreateAPIView):
#     """ Модель представления, которая позволяет создать Category в заметках """
#     model = GoalCategory
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = GoalCategoryCreateSerializer
#
# class GoalCategoryListView(ListAPIView):
#     """ Модель представления, которая позволяет просматривать все объекты Category """
#     model = GoalCategory
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = GoalCategorySerializer
#     pagination_class = LimitOffsetPagination
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter, ]
#     ordering_fields = ["title", "created"]
#     filterset_fields = ["user"]
#     ordering = ["title"]
#     search_fields = ["title"]
#
#     def get_queryset(self):
#         return GoalCategory.objects.select_related('user').filter(user=self.request.user).exclude(is_deleted=True)
#
#
# class GoalCategoryView(RetrieveUpdateDestroyAPIView):
#     """ Модель представления, которая позволяет редактировать и удалять объекты из Category """
#     model = GoalCategory
#     serializer_class = GoalCategorySerializer
#     permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]
#
#     def get_queryset(self):
#         return GoalCategory.objects.select_related('user').exclude(is_deleted=True)
#
#     def perform_destroy(self, instance):
#         with transaction.atomic():
#             instance.is_deleted = True
#             instance.save()
#             Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
#         return instance
#
# class GoalCreateView(CreateAPIView):
#     """ Модель представления, которая позволяет создавать объект Goal """
#     model = Goal
#     serializer_class = GoalCreateSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
# class GoalListView(ListAPIView):
#     """
#     Модель представления, которая позволяет выводить все объекты Goal.
#     Сортировать, фильтровать и искать по полям `title`, `description`
#     """
#     model = Goal
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = GoalSerializer
#     pagination_class = LimitOffsetPagination
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter, ]
#     filterset_class = GoalDateFilter
#     search_fields = ["title", "description"]
#     ordering_fields = ["due_date", "priority"]
#     ordering = ["priority", "due_date"]
#
#     def get_queryset(self):
#         return Goal.objects.select_related('user').filter(
#             user=self.request.user, category__is_deleted=False
#         ).exclude(status=Goal.Status.archived)
#
#
# class GoalView(RetrieveUpdateDestroyAPIView):
#     """ Модель представления, которая позволяет редактировать и удалять объекты Goal. """
#     model = Goal
#     serializer_class = GoalSerializer
#     permission_classes = [permissions.IsAuthenticated, GoalPermissions]
#
#     queryset = (
#         Goal.objects.select_related('user').filter(category__is_deleted=False).exclude(status=Goal.Status.archived)
#     )
#
#     def perform_destroy(self, instance):
#         instance.status = Goal.Status.archived
#         instance.save()
#         return instance
#
#
# class CommentCreateView(CreateAPIView):
#     """ Модель представления, которая позволяет создавать объекты Comment. """
#     model = GoalComment
#     serializer_class = CommentCreateSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# class CommentView(RetrieveUpdateDestroyAPIView):
#     """ Модель представления, которая позволяет редактировать и удалять объекты Comment. """
#     model = GoalComment
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticated, CommentPermissions]
#     queryset = GoalComment.objects.select_related('user')
#
#
# class CommentListView(ListAPIView):
#     """
#     Модель представления, которая позволяет выводить все объекты Comment.
#     Так же сортирую и делает фильтрацию по полю `goal`.
#     """
#     model = GoalComment
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = LimitOffsetPagination
#     filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
#     filterset_fields = ["goal"]
#     ordering = "-id"
#
#     def get_queryset(self):
#         return GoalComment.objects.select_related('user').filter(user=self.request.user)