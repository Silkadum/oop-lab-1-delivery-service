"""Позиция заказа."""


class OrderItem:
    """Позиция в корзине заказа: название товара, количество и цена.

    Цена запоминается в момент добавления, поэтому последующее
    изменение склада не меняет стоимость уже собранного заказа.
    """

    def __init__(self, name: str, quantity: int, price: float) -> None:
        name = name.strip()
        if not name:
            raise ValueError("Название позиции не может быть пустым")
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        if price <= 0:
            raise ValueError("Цена должна быть больше нуля")
        self.__name = name
        self.__quantity = quantity
        self.__price = price

    @property
    def name(self) -> str:
        return self.__name

    @property
    def quantity(self) -> int:
        return self.__quantity

    @property
    def price(self) -> float:
        return self.__price

    def add_quantity(self, quantity: int) -> None:
        """Увеличивает количество, если тот же товар добавили повторно."""
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        self.__quantity += quantity

    def total(self) -> float:
        """Возвращает стоимость позиции: количество × цена."""
        return self.__quantity * self.__price
