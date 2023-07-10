from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models import Goal, BoardParticipant
from tests.factories import BoardFactory, BoardParticipantFactory, CategoryFactory


@pytest.mark.django_db
class TestGoalCreateView:
    """ Тесты для Goal создать представление """
    url: str = reverse("goals:goal_create")

    def test_goal_create_owner_moderator(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, может ли новая цель быть
        успешно создана, когда пользователь является владельцем
        или модератором доски.
        """
        board = BoardFactory()
        category = CategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = auth_client.post(self.url, data=create_data)
        created_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Цель не создалась"
        assert created_goal, "Созданной цели не существует"

# ============ НЕ УВЕРЕН В ПРАВИЛЬНОСТИ РАБОТЫ ДАННЫХ ДВУХ ТЕСТОВ ==============================
    def test_goal_create_viewer(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, нельзя ли создать новую цель,
        когда пользователь является читатель доски.
        """
        board = BoardFactory()
        category = CategoryFactory(board=board)
        BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.reader
        )

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response = auth_client.post(self.url, data=create_data)
        unexpected_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Отказ в доступе не предоставлен"
        assert response.json() == {'category': ['Вы не создавали эту категорию']}, "Вы можете создать цель"
        assert not unexpected_goal, "Цель создана"

    def test_goal_create_deleted_category(self, auth_client, user, due_date) -> None:
        """
        Тест, чтобы проверить, нельзя ли создать новую цель в удаленной категории
        """
        board = BoardFactory()
        category = CategoryFactory(board=board, is_deleted=True)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response = auth_client.post(self.url, data=create_data)
        unexpected_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Отказ в доступе не предоставлен"
        assert response.json() == {'category': ['Не разрешено в удаленной категории']}
        assert not unexpected_goal, "Цель создана"

    def test_goal_create_deny(self, client) -> None:
        """
        Проверка того, что не аутентифицированные пользователи
        не могут получить доступ к конечной точке API создания цели.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"