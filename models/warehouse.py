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
        self.__address = address
        # Ключ — название товара в нижнем регистре, значение — (товар, остаток)
        self.__stock: dict[str, tuple[Product, int]] = {}

    @property
    def address(self) -> str:
        return self.__address

    def has_product(self, name: str) -> bool:
        return self._key(name) in self.__stock

    def find_product(self, name: str) -> Product:
        product, _ = self._get_entry(name)
        return product

    def get_quantity(self, name: str) -> int:
        _, quantity = self._get_entry(name)
        return quantity

    def get_stock(self) -> list[tuple[Product, int]]:
        """Возвращает пары (товар, остаток) для вывода на экран."""
        return list(self.__stock.values())

    def add_product(self, name: str, price: float, quantity: int) -> None:
        """Заводит на склад новый товар."""
        if self.has_product(name):
            raise ValueError(f"Товар «{name.strip()}» уже есть, пополните остаток")
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        self.__stock[self._key(name)] = (Product(name, price), quantity)

    def restock(self, name: str, quantity: int) -> None:
        """Пополняет остаток существующего товара."""
        product, available = self._get_entry(name)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        self.__stock[self._key(name)] = (product, available + quantity)

    def remove(self, name: str, quantity: int) -> None:
        """Убирает товар со склада. Если остаток стал нулевым, товар удаляется."""
        product, available = self._get_entry(name)
        if quantity <= 0:
            raise ValueError("Количество должно быть больше нуля")
        if quantity > available:
            raise ValueError(f"На складе только {available} шт.")
        key = self._key(name)
        if quantity == available:
            del self.__stock[key]
        else:
            self.__stock[key] = (product, available - quantity)

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

    # ----- Вспомогательные методы -----

    def _get_entry(self, name: str) -> tuple[Product, int]:
        """Возвращает пару (товар, остаток) или ValueError, если товара нет."""
        key = self._key(name)
        if key not in self.__stock:
            raise ValueError(f"Товара «{name.strip()}» нет на складе")
        return self.__stock[key]

    @staticmethod
    def _key(name: str) -> str:
        return name.strip().lower()
