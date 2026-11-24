"""Склад магазина."""

from models.order_item import OrderItem
from models.product import Product


class Warehouse:
    """Склад: товары, их остатки и адрес, по которому работает самовывоз.

    Название товара не зависит от регистра: «Мышь» и «мышь» — один товар.
    """

    def __init__(self, address: str) -> None:
        address = address.strip()
        if not address:
            raise ValueError("Адрес склада не может быть пустым")
        self._address = address
        # Ключ словарей — название товара в нижнем регистре
        self._products: dict[str, Product] = {}
        self._quantities: dict[str, int] = {}

    @property
    def address(self) -> str:
        return self._address

    def has_product(self, name: str) -> bool:
        return self._key(name) in self._products

    def find_product(self, name: str) -> Product:
        key = self._key(name)
        if key not in self._products:
            raise ValueError(f"Товара «{name.strip()}» нет на складе")
        return self._products[key]

    def get_quantity(self, name: str) -> int:
        self.find_product(name)
        return self._quantities[self._key(name)]

    def get_stock(self) -> list[tuple[Product, int]]:
        """Возвращает пары (товар, остаток) для вывода на экран."""
        return [
            (product, self._quantities[key])
            for key, product in self._products.items()
        ]

    def add_product(self, name: str, price: float, quantity: int) -> None:
        """Заводит на склад новый товар."""
        if self.has_product(name):
            raise ValueError(f"Товар «{name.strip()}» уже есть, пополните остаток")
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        product = Product(name, price)
        key = self._key(name)
        self._products[key] = product
        self._quantities[key] = quantity

    def restock(self, name: str, quantity: int) -> None:
        """Пополняет остаток существующего товара."""
        self.find_product(name)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        self._quantities[self._key(name)] += quantity

    def remove(self, name: str, quantity: int) -> None:
        """Убирает товар со склада. Если остаток стал нулевым, товар удаляется."""
        available = self.get_quantity(name)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        if quantity > available:
            raise ValueError(f"На складе только {available} шт.")
        key = self._key(name)
        self._quantities[key] -= quantity
        if self._quantities[key] == 0:
            del self._products[key]
            del self._quantities[key]

    def take_items(self, items: tuple[OrderItem, ...]) -> None:
        """Списывает позиции заказа. Либо списывается всё, либо ничего."""
        # Сначала проверяем все позиции, чтобы не списать заказ наполовину
        for item in items:
            if not self.has_product(item.name):
                raise ValueError(f"Товара «{item.name}» больше нет на складе")
            available = self.get_quantity(item.name)
            if item.quantity > available:
                raise ValueError(
                    f"Товара «{item.name}» не хватает: "
                    f"в заказе {item.quantity} шт., на складе {available} шт."
                )
        for item in items:
            self.remove(item.name, item.quantity)

    def return_items(self, items: tuple[OrderItem, ...]) -> None:
        """Возвращает позиции отменённого заказа на склад."""
        for item in items:
            if self.has_product(item.name):
                self.restock(item.name, item.quantity)
            else:
                # Товар успели удалить со склада — заводим его заново
                self.add_product(item.name, item.price, item.quantity)

    @staticmethod
    def _key(name: str) -> str:
        return name.strip().lower()
