"""Заказ — центральная сущность программы."""

from delivery.delivery_method import DeliveryMethod
from models.courier import Courier
from models.customer import Customer
from models.order_item import OrderItem
from models.order_status import OrderStatus


class Order:
    """Заказ: клиент, адрес, позиции, способ доставки, курьер и статус.

    Все изменения проходят через методы, которые проверяют,
    допустима ли операция в текущем состоянии заказа.
    """

    # Из какого статуса в какие можно перейти
    _TRANSITIONS = {
        OrderStatus.NEW: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [
            OrderStatus.IN_TRANSIT,
            OrderStatus.READY_FOR_PICKUP,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.IN_TRANSIT: [OrderStatus.COMPLETED],
        OrderStatus.READY_FOR_PICKUP: [
            OrderStatus.COMPLETED,
            OrderStatus.CANCELLED,
        ],
        OrderStatus.COMPLETED: [],
        OrderStatus.CANCELLED: [],
    }

    def __init__(self, order_id: int, customer: Customer, address: str) -> None:
        address = address.strip()
        if order_id <= 0:
            raise ValueError("Номер заказа должен быть положительным")
        if not address:
            raise ValueError("Адрес доставки не может быть пустым")
        self._order_id = order_id
        self._customer = customer
        self._address = address
        self._items: list[OrderItem] = []
        self._delivery_method: DeliveryMethod | None = None
        self._courier: Courier | None = None
        self._status = OrderStatus.NEW

    @property
    def order_id(self) -> int:
        return self._order_id

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def address(self) -> str:
        return self._address

    @property
    def items(self) -> tuple[OrderItem, ...]:
        # Кортеж, чтобы список позиций нельзя было изменить снаружи
        return tuple(self._items)

    @property
    def delivery_method(self) -> DeliveryMethod | None:
        return self._delivery_method

    @property
    def courier(self) -> Courier | None:
        return self._courier

    @property
    def status(self) -> OrderStatus:
        return self._status

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
            self._items.append(item)

    def remove_item(self, name: str) -> None:
        """Удаляет позицию из корзины по названию товара."""
        self._require_new("Менять состав можно только у нового заказа")
        item = self._find_item(name)
        if item is None:
            raise ValueError(f"В заказе нет товара «{name}»")
        self._items.remove(item)

    # ----- Доставка и курьер -----

    def set_delivery_method(self, method: DeliveryMethod) -> None:
        """Выбирает способ доставки. Курьер снимается, если он больше не нужен."""
        self._require_new("Способ доставки можно менять только у нового заказа")
        if not method.requires_courier and self._courier is not None:
            self._courier.release()
            self._courier = None
        self._delivery_method = method

    def assign_courier(self, courier: Courier) -> None:
        """Назначает курьера, если способ доставки этого требует."""
        if self._status not in (OrderStatus.NEW, OrderStatus.CONFIRMED):
            raise ValueError("Курьера можно назначить только до отправки заказа")
        if self._delivery_method is None:
            raise ValueError("Сначала выберите способ доставки")
        if not self._delivery_method.requires_courier:
            raise ValueError(
                f"Для способа «{self._delivery_method.name}» курьер не нужен"
            )
        if self._courier is not None:
            raise ValueError(f"На заказ уже назначен курьер {self._courier.name}")
        courier.take_order()
        self._courier = courier

    # ----- Стоимость -----

    def items_cost(self) -> float:
        return sum(item.total() for item in self._items)

    def delivery_cost(self) -> float:
        if self._delivery_method is None:
            return 0.0
        return self._delivery_method.calculate_cost(self.items_cost())

    def total_cost(self) -> float:
        return self.items_cost() + self.delivery_cost()

    # ----- Статусы -----

    def allowed_statuses(self) -> list[OrderStatus]:
        """Возвращает статусы, в которые заказ может перейти по своему типу доставки."""
        result = []
        for status in self._TRANSITIONS[self._status]:
            if status == OrderStatus.IN_TRANSIT and not self._needs_courier():
                continue
            if status == OrderStatus.READY_FOR_PICKUP and self._needs_courier():
                continue
            result.append(status)
        return result

    def check_status_change(self, new_status: OrderStatus) -> None:
        """Проверяет переход в новый статус. Если он недопустим — ValueError."""
        if new_status not in self.allowed_statuses():
            raise ValueError(
                f"Нельзя перевести заказ из статуса «{self._status.value}» "
                f"в «{new_status.value}»"
            )
        if new_status == OrderStatus.CONFIRMED:
            if not self._items:
                raise ValueError("Нельзя подтвердить заказ без позиций")
            if self._delivery_method is None:
                raise ValueError("Нельзя подтвердить заказ без способа доставки")
        if new_status == OrderStatus.IN_TRANSIT and self._courier is None:
            raise ValueError("Сначала назначьте курьера")

    def change_status(self, new_status: OrderStatus) -> None:
        """Переводит заказ в новый статус после проверки."""
        self.check_status_change(new_status)
        self._status = new_status
        finished = (OrderStatus.COMPLETED, OrderStatus.CANCELLED)
        if new_status in finished and self._courier is not None:
            self._courier.release()

    # ----- Вспомогательные методы -----

    def _find_item(self, name: str) -> OrderItem | None:
        key = name.strip().lower()
        for item in self._items:
            if item.name.lower() == key:
                return item
        return None

    def _require_new(self, message: str) -> None:
        if self._status != OrderStatus.NEW:
            raise ValueError(message)

    def _needs_courier(self) -> bool:
        # Пока способ не выбран, считаем, что курьер нужен
        if self._delivery_method is None:
            return True
        return self._delivery_method.requires_courier
