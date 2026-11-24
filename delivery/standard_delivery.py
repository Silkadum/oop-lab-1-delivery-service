"""Стандартная доставка курьером."""

from constants import STANDARD_BASE_COST, STANDARD_FREE_FROM
from delivery.delivery_method import DeliveryMethod


class StandardDelivery(DeliveryMethod):
    """Фиксированная цена, бесплатно для заказов от определённой суммы."""

    name = "Стандартная доставка"
    requires_courier = True

    def calculate_cost(self, items_cost: float) -> float:
        if items_cost >= STANDARD_FREE_FROM:
            return 0.0
        return STANDARD_BASE_COST

    def estimate_time(self) -> str:
        return "3–5 дней"
