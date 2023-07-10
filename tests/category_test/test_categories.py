from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models import BoardParticipant
from goals.models import GoalCategory
from tests.factories import BoardFactory, BoardParticipantFactory


@pytest.mark.django_db
class TestCategoryCreateView:
    """Тесты для GoalCategory создают представление"""
    url: str = reverse("goals:category_create")

    def test_category_create_owner_moderator(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, может ли новая категория быть успешно создана,
        когда пользователь является владельцем или модератором доски.
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Owner category",
        }

        response: Response = auth_client.post(self.url, data=create_data)
        created_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Категория не создалась"
        assert created_category, "Созданной категории не существует"

    # ================================================================
    def test_category_create_viewer(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, не может ли быть создана новая категория,
        когда пользователь является читателем доски.
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user, role=BoardParticipant.Role.reader)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Viewer category",
        }

        response = auth_client.post(self.url, data=create_data)
        unexpected_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Отказ в доступе не предоставлен"
        assert response.json() == {'board': ['Вы должны быть владельцем или редактором']}, "Вы можете создать категорию"
        assert not unexpected_category, "Категория создана"

    def test_category_create_deleted_board(self, auth_client, user) -> None:
        """
        Тест, чтобы проверить, нельзя ли создать новую категорию на удаленной доске.
        """
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Deleted board category",
        }

        response = auth_client.post(self.url, data=create_data)
        unexpected_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Отказ в доступе не предоставлен"
        assert response.json() == {'board': ['Не разрешено в удаленном объекте']}, "Вы можете создать категорию"
        assert not unexpected_category, "Категория создана"

    def test_category_create_deny(self, client) -> None:
        """
        Убедитесь, что пользователи, не прошедшие проверку подлинности,
        не могут получить доступ к конечной точке API создания категории.
        """
        response: Response = client.post(self.url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, "Отказ в доступе не предоставлен"