"""Стандартная доставка курьером."""

from delivery.delivery_method import DeliveryMethod


class StandardDelivery(DeliveryMethod):
    """Фиксированная цена, бесплатно для заказов от определённой суммы."""

    BASE_COST = 300.0
    FREE_FROM = 5000.0

    @property
    def name(self) -> str:
        return "Стандартная доставка"

    def calculate_cost(self, items_cost: float) -> float:
        if items_cost >= self.FREE_FROM:
            return 0.0
        return self.BASE_COST

    def estimate_time(self) -> str:
        return "3–5 дней"
