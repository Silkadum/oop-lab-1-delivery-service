"""Общий контракт способа доставки."""

from abc import ABC, abstractmethod


class DeliveryMethod(ABC):
    """Абстрактный способ доставки.

    Каждый наследник по-своему считает стоимость и срок, поэтому
    заказу не нужно проверять, какой именно способ выбран.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Название способа доставки для пользователя."""

    @property
    def requires_courier(self) -> bool:
        """Нужен ли курьер. По умолчанию нужен, самовывоз переопределяет."""
        return True

    @abstractmethod
    def calculate_cost(self, items_cost: float) -> float:
        """Возвращает стоимость доставки по сумме товаров в заказе."""

    @abstractmethod
    def estimate_time(self) -> str:
        """Возвращает ориентировочный срок доставки."""
