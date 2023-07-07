from django.db import models
from django.utils import timezone

from core.models import User


class DatesModelMixin(models.Model):
    """ Модель для получения даты создания и даты редактирования объекта """
    created = models.DateTimeField(verbose_name="Дата создания")
    updated = models.DateTimeField(verbose_name="Дата последнего обновления")

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class GoalCategory(DatesModelMixin):
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    """ Модель создания Категории для заметок """
    board = models.ForeignKey("Board", verbose_name="Доска ", on_delete=models.PROTECT, related_name="categories")
    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    # def save(self, *args, **kwargs):
    #     if not self.pk:  # if not self.id: # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.title)


class Goal(DatesModelMixin):
    """ Модель создания заметки.
    Статус:
        :param: 'to_do' - К выполнению
        :param: 'in_progress' - В процессе
        :param: 'done' - Выполнено
        :param: 'archived' - Архив
    Приоритет:
        :param: 'low' - Низкий
        :param: 'medium' - Средний
        :param: 'high' - Высокий
        :param: 'critical' - Критический
    """
    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    status = models.PositiveSmallIntegerField(verbose_name="Статус", choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name="Приоритет", choices=Priority.choices,
                                                default=Priority.medium)
    user = models.ForeignKey(User, verbose_name="Автор", related_name="goals", on_delete=models.PROTECT)
    category = models.ForeignKey(GoalCategory, verbose_name="Категория", on_delete=models.PROTECT)
    title = models.CharField(verbose_name="Заголовок цели", max_length=255)
    description = models.TextField(verbose_name="Описание", null=True, blank=True, default=None)
    due_date = models.DateField(verbose_name="Дата выполнения", null=True, blank=True, default=None)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"


class GoalComment(DatesModelMixin):
    """ Модель создания объекта `comment` для модели заметок `goal` """
    goal = models.ForeignKey(Goal, verbose_name="Цель", related_name="goal_comments", on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Автор ", related_name="goal_comments", on_delete=models.PROTECT)
    text = models.TextField(verbose_name="Текст")

    def __str__(self):
        return '{}: {}'.format(self.user, self.goal)

    class Meta:
        verbose_name = "Комментарий к цели"
        verbose_name_plural = "Комментарии к целям"


class Board(DatesModelMixin):
    """ Модель для работы с объекта `board` """
    title = models.CharField(verbose_name="Название", max_length=255)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    def __str__(self):
        return '{}'.format(self.title)

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"


class BoardParticipant(DatesModelMixin):
    """ Модель позволяющая выбирать и назначать права пользователям """
    class Role(models.IntegerChoices):
        owner = 1, "Владелец"
        writer = 2, "Редактор"
        reader = 3, "Читатель"

    editable_choices = Role.choices
    editable_choices.pop(0)

    board = models.ForeignKey(Board, verbose_name="Доска", on_delete=models.PROTECT, related_name="participants")
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.PROTECT, related_name="participants")
    role = models.PositiveSmallIntegerField(verbose_name="Роль", choices=Role.choices, default=Role.owner)

    def __str__(self):
        return '{}: {}'.format(self.board, self.user)

    class Meta:
        unique_together = ("board", "user")
        verbose_name = "Участник"
        verbose_name_plural = "Участники"