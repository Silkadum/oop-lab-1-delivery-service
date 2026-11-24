"""Самовывоз со склада."""

from delivery.delivery_method import DeliveryMethod


class Pickup(DeliveryMethod):
    """Клиент забирает заказ сам: бесплатно и без курьера."""

    @property
    def name(self) -> str:
        return "Самовывоз"

    @property
    def requires_courier(self) -> bool:
        return False

    def calculate_cost(self, items_cost: float) -> float:
        return 0.0

    def estimate_time(self) -> str:
        return "готов к выдаче через 2 часа"
