from dataclasses import field
from typing import ClassVar, Type, List, Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, EXCLUDE


@dataclass
class MessageFrom:
    """ Сообщение от пользователя """
    id: int
    first_name: str
    last_name: Optional[str]
    username: str

    class Meta:
        unknown = EXCLUDE


@dataclass
class Chat:
    """ Чат пользователя """
    id: int
    type: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    title: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class Message:
    """ Сообщения """
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})
    chat: Chat
    text: Optional[str] = None

    class Meta:
        unknown = EXCLUDE


@dataclass
class UpdateObj:
    """ Обновить объект """
    update_id: int
    message: Message

    class Meta:
        unknown = EXCLUDE


@dataclass
class GetUpdatesResponse:
    """ Получить ответ об обновлениях """
    ok: bool
    result: List[UpdateObj]

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@dataclass
class SendMessageResponse:
    """ Отправить сообщение Ответ """
    ok: bool
    result: Message

    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE