"""Заказ — центральная сущность программы."""

from constants import (
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_IN_TRANSIT,
    STATUS_NEW,
    STATUS_READY_FOR_PICKUP,
)
from delivery.delivery_method import DeliveryMethod
from models.courier import Courier
from models.customer import Customer
from models.order_item import OrderItem


class Order:
    """Заказ: клиент, адрес, позиции, способ доставки, курьер и статус.

    Все изменения проходят через методы, которые проверяют,
    допустима ли операция в текущем состоянии заказа.
    """

    # Из какого статуса в какие можно перейти
    _TRANSITIONS = {
        STATUS_NEW: [STATUS_CONFIRMED, STATUS_CANCELLED],
        STATUS_CONFIRMED: [
            STATUS_IN_TRANSIT,
            STATUS_READY_FOR_PICKUP,
            STATUS_CANCELLED,
        ],
        STATUS_IN_TRANSIT: [STATUS_COMPLETED],
        STATUS_READY_FOR_PICKUP: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_COMPLETED: [],
        STATUS_CANCELLED: [],
    }

    def __init__(self, order_id: int, customer: Customer, address: str) -> None:
        address = address.strip()
        if order_id <= 0:
            raise ValueError("Номер заказа должен быть положительным")
        if not address:
            raise ValueError("Адрес доставки не может быть пустым")
        self.__order_id = order_id
        self.__customer = customer
        self.__address = address
        self.__items: list[OrderItem] = []
        self.__delivery_method: DeliveryMethod | None = None
        self.__courier: Courier | None = None
        self.__status = STATUS_NEW

    @property
    def order_id(self) -> int:
        return self.__order_id

    @property
    def customer(self) -> Customer:
        return self.__customer

    @property
    def address(self) -> str:
        return self.__address

    @property
    def items(self) -> tuple[OrderItem, ...]:
        # Кортеж, чтобы список позиций нельзя было изменить снаружи
        return tuple(self.__items)

    @property
    def delivery_method(self) -> DeliveryMethod | None:
        return self.__delivery_method

    @property
    def courier(self) -> Courier | None:
        return self.__courier

    @property
    def status(self) -> str:
        return self.__status

    # ----- Корзина -----

    def quantity_of(self, name: str) -> int:
        """Возвращает, сколько единиц товара уже лежит в корзине."""
        item = self._find_item(name)
        return item.quantity if item is not None else 0

    def add_item(self, item: OrderItem) -> None:
        """Добавляет позицию. Повторный товар увеличивает количество."""
        self._require_new("Менять состав можно только у нового заказа")
        existing = self._find_item(item.name)
        if existing is not None:
            existing.add_quantity(item.quantity)
        else:
            self.__items.append(item)

    def remove_item(self, name: str) -> None:
        """Удаляет позицию из корзины по названию товара."""
        self._require_new("Менять состав можно только у нового заказа")
        item = self._find_item(name)
        if item is None:
            raise ValueError(f"В заказе нет товара «{name}»")
        self.__items.remove(item)

    # ----- Доставка и курьер -----

    def set_delivery_method(self, method: DeliveryMethod) -> None:
        """Выбирает способ доставки. Курьер снимается, если он больше не нужен."""
        self._require_new("Способ доставки можно менять только у нового заказа")
        if not method.requires_courier and self.__courier is not None:
            self.__courier.release()
            self.__courier = None
        self.__delivery_method = method

    def assign_courier(self, courier: Courier) -> None:
        """Назначает курьера, если способ доставки этого требует."""
        if self.__status not in (STATUS_NEW, STATUS_CONFIRMED):
            raise ValueError("Курьера можно назначить только до отправки заказа")
        if self.__delivery_method is None:
            raise ValueError("Сначала выберите способ доставки")
        if not self.__delivery_method.requires_courier:
            raise ValueError(
                f"Для способа «{self.__delivery_method.name}» курьер не нужен"
            )
        if self.__courier is not None:
            raise ValueError(f"На заказ уже назначен курьер {self.__courier.name}")
        courier.take_order()
        self.__courier = courier

    # ----- Стоимость -----

    def items_cost(self) -> float:
        return sum(item.total() for item in self.__items)

    def delivery_cost(self) -> float:
        if self.__delivery_method is None:
            return 0.0
        return self.__delivery_method.calculate_cost(self.items_cost())

    def total_cost(self) -> float:
        return self.items_cost() + self.delivery_cost()

    # ----- Статусы -----

    def allowed_statuses(self) -> list[str]:
        """Возвращает статусы, в которые заказ может перейти по своему типу доставки."""
        result = []
        for status in self._TRANSITIONS[self.__status]:
            if status == STATUS_IN_TRANSIT and not self._needs_courier():
                continue
            if status == STATUS_READY_FOR_PICKUP and self._needs_courier():
                continue
            result.append(status)
        return result

    def check_status_change(self, new_status: str) -> None:
        """Проверяет переход в новый статус. Если он недопустим — ValueError."""
        if new_status not in self.allowed_statuses():
            raise ValueError(
                f"Нельзя перевести заказ из статуса «{self.__status}» "
                f"в «{new_status}»"
            )
        if new_status == STATUS_CONFIRMED:
            if not self.__items:
                raise ValueError("Нельзя подтвердить заказ без позиций")
            if self.__delivery_method is None:
                raise ValueError("Нельзя подтвердить заказ без способа доставки")
        if new_status == STATUS_IN_TRANSIT and self.__courier is None:
            raise ValueError("Сначала назначьте курьера")

    def change_status(self, new_status: str) -> None:
        """Переводит заказ в новый статус после проверки."""
        self.check_status_change(new_status)
        self.__status = new_status
        finished = (STATUS_COMPLETED, STATUS_CANCELLED)
        if new_status in finished and self.__courier is not None:
            self.__courier.release()

    # ----- Вспомогательные методы -----

    def _find_item(self, name: str) -> OrderItem | None:
        key = name.strip().lower()
        for item in self.__items:
            if item.name.lower() == key:
                return item
        return None

    def _require_new(self, message: str) -> None:
        if self.__status != STATUS_NEW:
            raise ValueError(message)

    def _needs_courier(self) -> bool:
        # Пока способ не выбран, считаем, что курьер нужен
        if self.__delivery_method is None:
            return True
        return self.__delivery_method.requires_courier
