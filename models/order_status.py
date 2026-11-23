"""Статусы заказа."""

from enum import Enum


class OrderStatus(Enum):
    """Возможные статусы заказа. Значение — текст для пользователя."""

    NEW = "новый"
    CONFIRMED = "подтверждён"
    IN_TRANSIT = "в пути"
    READY_FOR_PICKUP = "готов к выдаче"
    COMPLETED = "выполнен"
    CANCELLED = "отменён"
