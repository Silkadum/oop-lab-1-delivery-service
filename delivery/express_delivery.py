"""Экспресс-доставка курьером."""

from constants import EXPRESS_BASE_COST, EXPRESS_PERCENT
from delivery.delivery_method import DeliveryMethod


class ExpressDelivery(DeliveryMethod):
    """Базовая цена плюс процент от суммы товаров, зато быстро."""

    name = "Экспресс-доставка"
    requires_courier = True

    def calculate_cost(self, items_cost: float) -> float:
        return EXPRESS_BASE_COST + items_cost * EXPRESS_PERCENT

    def estimate_time(self) -> str:
        return "1 день"
