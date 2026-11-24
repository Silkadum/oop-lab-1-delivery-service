"""Экспресс-доставка курьером."""

from delivery.delivery_method import DeliveryMethod


class ExpressDelivery(DeliveryMethod):
    """Базовая цена плюс процент от суммы товаров, зато быстро."""

    BASE_COST = 500.0
    PERCENT = 0.05

    @property
    def name(self) -> str:
        return "Экспресс-доставка"

    def calculate_cost(self, items_cost: float) -> float:
        return self.BASE_COST + items_cost * self.PERCENT

    def estimate_time(self) -> str:
        return "1 день"
