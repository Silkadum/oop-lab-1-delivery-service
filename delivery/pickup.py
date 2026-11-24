"""Самовывоз со склада."""

from constants import PICKUP_COST
from delivery.delivery_method import DeliveryMethod


class Pickup(DeliveryMethod):
    """Клиент забирает заказ сам: бесплатно и без курьера."""

    name = "Самовывоз"
    requires_courier = False

    def calculate_cost(self, items_cost: float) -> float:
        return PICKUP_COST

    def estimate_time(self) -> str:
        return "готов к выдаче через 2 часа"
