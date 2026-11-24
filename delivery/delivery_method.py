"""Общий контракт способа доставки."""

from abc import ABC, abstractmethod


class DeliveryMethod(ABC):
    """Абстрактный способ доставки.

    Каждый наследник задаёт атрибуты name и requires_courier
    и по-своему считает стоимость и срок, поэтому заказу не нужно
    проверять, какой именно способ выбран.
    """

    name: str                 # название способа для пользователя
    requires_courier: bool    # нужен ли курьер

    @abstractmethod
    def calculate_cost(self, items_cost: float) -> float:
        """Возвращает стоимость доставки по сумме товаров в заказе."""

    @abstractmethod
    def estimate_time(self) -> str:
        """Возвращает ориентировочный срок доставки."""
