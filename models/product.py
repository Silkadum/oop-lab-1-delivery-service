"""Товар, который хранится на складе."""


class Product:
    """Товар: название и цена за единицу.

    Товары создаются только на складе, покупатель выбирает
    из уже существующих.
    """

    def __init__(self, name: str, price: float) -> None:
        name = name.strip()
        if not name:
            raise ValueError("Название товара не может быть пустым")
        if price <= 0:
            raise ValueError("Цена товара должна быть больше нуля")
        self._name = name
        self._price = price

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price
