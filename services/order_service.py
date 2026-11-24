"""Сервис управления заказами (бизнес-логика без ввода и вывода)."""

from delivery.delivery_method import DeliveryMethod
from delivery.express_delivery import ExpressDelivery
from delivery.pickup import Pickup
from delivery.standard_delivery import StandardDelivery
from models.courier import Courier
from models.customer import Customer
from models.order import Order
from models.order_item import OrderItem
from models.order_status import OrderStatus
from models.warehouse import Warehouse


class OrderService:
    """Хранит заказы и курьеров в памяти и выполняет операции над ними.

    Связывает заказы со складом: товар списывается при подтверждении
    заказа и возвращается при отмене.
    """

    def __init__(self, warehouse: Warehouse) -> None:
        self._warehouse = warehouse
        self._orders: dict[int, Order] = {}
        self._couriers: dict[int, Courier] = {}
        self._next_order_id = 1
        self._next_courier_id = 1
        self._delivery_methods: tuple[DeliveryMethod, ...] = (
            StandardDelivery(),
            ExpressDelivery(),
            Pickup(),
        )

    # ----- Заказы -----

    def create_order(self, name: str, phone: str, address: str) -> Order:
        """Создаёт пустой заказ с новым номером."""
        customer = Customer(name, phone)
        order = Order(self._next_order_id, customer, address)
        self._orders[order.order_id] = order
        self._next_order_id += 1
        return order

    def get_orders(self) -> list[Order]:
        return list(self._orders.values())

    def find_order(self, order_id: int) -> Order:
        if order_id not in self._orders:
            raise ValueError(f"Заказа №{order_id} не существует")
        return self._orders[order_id]

    def add_item(self, order_id: int, product_name: str, quantity: int) -> None:
        """Кладёт товар со склада в корзину, если его хватает.

        На этом шаге остаток только проверяется, а списывается
        при подтверждении заказа.
        """
        order = self.find_order(order_id)
        product = self._warehouse.find_product(product_name)
        available = self._warehouse.get_quantity(product.name)
        in_cart = order.quantity_of(product.name)
        if in_cart >= available:
            raise ValueError(f"Весь остаток товара «{product.name}» уже в корзине")
        if in_cart + quantity > available:
            raise ValueError(
                f"Можно добавить не больше {available - in_cart} шт. "
                f"товара «{product.name}»"
            )
        order.add_item(OrderItem(product.name, quantity, product.price))

    def remove_item(self, order_id: int, product_name: str) -> None:
        self.find_order(order_id).remove_item(product_name)

    # ----- Доставка и курьеры -----

    def get_delivery_methods(self) -> tuple[DeliveryMethod, ...]:
        return self._delivery_methods

    def set_delivery_method(self, order_id: int, method: DeliveryMethod) -> None:
        self.find_order(order_id).set_delivery_method(method)

    def add_courier(self, name: str, phone: str) -> Courier:
        courier = Courier(self._next_courier_id, name, phone)
        self._couriers[courier.courier_id] = courier
        self._next_courier_id += 1
        return courier

    def get_free_couriers(self) -> list[Courier]:
        return [c for c in self._couriers.values() if c.is_free]

    def assign_courier(self, order_id: int, courier_id: int) -> None:
        order = self.find_order(order_id)
        if courier_id not in self._couriers:
            raise ValueError(f"Курьера №{courier_id} не существует")
        order.assign_courier(self._couriers[courier_id])

    # ----- Статусы -----

    def change_status(self, order_id: int, new_status: OrderStatus) -> None:
        """Меняет статус заказа и синхронизирует склад."""
        order = self.find_order(order_id)
        # Проверяем переход до работы со складом, чтобы не списать товар зря
        order.check_status_change(new_status)
        if new_status == OrderStatus.CONFIRMED:
            self._warehouse.take_items(order.items)
        elif (
            new_status == OrderStatus.CANCELLED
            and order.status != OrderStatus.NEW
        ):
            # Товар списан только после подтверждения, его и возвращаем
            self._warehouse.return_items(order.items)
        order.change_status(new_status)
