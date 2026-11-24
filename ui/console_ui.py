"""Консольный интерфейс: меню, ввод и вывод."""

from models.order import Order
from models.warehouse import Warehouse
from services.order_service import OrderService


class ConsoleUI:
    """Взаимодействие с пользователем через консоль.

    Здесь только ввод, вывод и проверка формата ввода. Все правила
    предметной области проверяют модели и сервис, а их ошибки
    (ValueError) показываются пользователю как сообщения.
    """

    def __init__(self, service: OrderService, warehouse: Warehouse) -> None:
        self._service = service
        self._warehouse = warehouse
        # Пункт меню -> (текст, метод-обработчик)
        self._menu = {
            "1": ("Создать заказ", self._create_order),
            "2": ("Показать все заказы", self._show_orders),
            "3": ("Изменить корзину заказа", self._edit_cart),
            "4": ("Выбрать способ доставки", self._choose_delivery),
            "5": ("Назначить курьера", self._assign_courier),
            "6": ("Изменить статус заказа", self._change_status),
            "7": ("Показать склад", self._show_stock),
            "8": ("Добавить товар на склад", self._add_to_stock),
            "9": ("Убрать товар со склада", self._remove_from_stock),
        }

    def run(self) -> None:
        """Запускает меню. Ctrl+C и Ctrl+D завершают работу без трассировки."""
        try:
            self._loop()
        except (KeyboardInterrupt, EOFError):
            print("\nРабота завершена.")

    def _loop(self) -> None:
        """Главный цикл: работает, пока пользователь не выберет выход."""
        while True:
            print("\n===== Служба доставки =====")
            for key, (title, _) in self._menu.items():
                print(f"{key}. {title}")
            print("0. Выход")
            choice = input("Выберите пункт: ").strip()
            if choice == "0":
                print("Работа завершена.")
                break
            if choice not in self._menu:
                print("Такого пункта нет, попробуйте ещё раз.")
                continue
            _, action = self._menu[choice]
            try:
                action()
            except ValueError as error:
                print(f"Ошибка: {error}")

    # ----- Пункты меню -----

    def _create_order(self) -> None:
        name = self._read_text("Имя клиента: ")
        phone = self._read_text("Телефон клиента: ")
        address = self._read_text("Адрес доставки: ")
        order = self._service.create_order(name, phone, address)
        print(f"Создан заказ №{order.order_id}. Добавьте товары.")
        self._fill_cart(order)
        if not order.items:
            print("Корзина пуста. Товары можно добавить через пункт 3.")
        self._print_order(order)

    def _show_orders(self) -> None:
        orders = self._service.get_orders()
        if not orders:
            print("Заказов пока нет.")
            return
        for order in orders:
            self._print_order(order)

    def _edit_cart(self) -> None:
        order = self._ask_order()
        while True:
            self._print_order(order)
            print("1. Добавить товар")
            print("2. Удалить позицию")
            print("0. Назад")
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                return
            try:
                if choice == "1":
                    self._fill_cart(order)
                elif choice == "2":
                    name = self._read_text("Название товара для удаления: ")
                    self._service.remove_item(order.order_id, name)
                    print("Позиция удалена.")
                else:
                    print("Такого действия нет.")
            except ValueError as error:
                print(f"Ошибка: {error}")

    def _choose_delivery(self) -> None:
        order = self._ask_order()
        methods = self._service.get_delivery_methods()
        items_cost = order.items_cost()
        print("Способы доставки для этого заказа:")
        for number, method in enumerate(methods, start=1):
            cost = method.calculate_cost(items_cost)
            print(
                f"{number}. {method.name}: {cost:.2f} руб., "
                f"срок — {method.estimate_time()}"
            )
        index = self._read_choice("Номер способа (0 — отмена): ", len(methods))
        if index is None:
            return
        method = methods[index]
        self._service.set_delivery_method(order.order_id, method)
        print(
            f"Выбрано: {method.name}. Стоимость доставки "
            f"{order.delivery_cost():.2f} руб., срок — {method.estimate_time()}."
        )
        print(f"Итого по заказу: {order.total_cost():.2f} руб.")

    def _assign_courier(self) -> None:
        order = self._ask_order()
        couriers = self._service.get_free_couriers()
        if not couriers:
            print("Свободных курьеров нет.")
            return
        print("Свободные курьеры:")
        for number, courier in enumerate(couriers, start=1):
            print(f"{number}. {courier.name}, {courier.phone}")
        index = self._read_choice("Номер курьера (0 — отмена): ", len(couriers))
        if index is None:
            return
        courier = couriers[index]
        self._service.assign_courier(order.order_id, courier.courier_id)
        print(f"Курьер {courier.name} назначен на заказ №{order.order_id}.")

    def _change_status(self) -> None:
        order = self._ask_order()
        statuses = order.allowed_statuses()
        print(f"Текущий статус: {order.status.value}")
        if not statuses:
            print("Заказ завершён, статус больше не меняется.")
            return
        for number, status in enumerate(statuses, start=1):
            print(f"{number}. {status.value}")
        index = self._read_choice("Новый статус (0 — отмена): ", len(statuses))
        if index is None:
            return
        self._service.change_status(order.order_id, statuses[index])
        print("Статус изменён.")
        self._print_order(order)

    def _show_stock(self) -> None:
        print(f"Склад (адрес самовывоза: {self._warehouse.address}):")
        stock = self._warehouse.get_stock()
        if not stock:
            print("  склад пуст")
            return
        for product, quantity in stock:
            print(f"  {product.name} — {quantity} шт., {product.price:.2f} руб./шт.")

    def _add_to_stock(self) -> None:
        self._show_stock()
        name = self._read_text("Название товара: ")
        if self._warehouse.has_product(name):
            quantity = self._read_int("Сколько добавить: ")
            self._warehouse.restock(name, quantity)
            print("Остаток пополнен.")
        else:
            price = self._read_float("Цена за единицу: ")
            quantity = self._read_int("Количество: ")
            self._warehouse.add_product(name, price, quantity)
            print("Товар добавлен на склад.")

    def _remove_from_stock(self) -> None:
        self._show_stock()
        name = self._read_text("Название товара: ")
        quantity = self._read_int("Сколько убрать: ")
        self._warehouse.remove(name, quantity)
        print("Товар убран со склада.")

    # ----- Вспомогательные методы -----

    def _fill_cart(self, order: Order) -> None:
        """Добавляет товары в корзину, пока пользователь не введёт 0."""
        while True:
            self._show_stock()
            name = self._read_text("Название товара (0 — закончить): ")
            if name == "0":
                return
            quantity = self._read_int("Количество: ")
            try:
                self._service.add_item(order.order_id, name, quantity)
                print("Товар добавлен в корзину.")
            except ValueError as error:
                print(f"Ошибка: {error}")

    def _ask_order(self) -> Order:
        order_id = self._read_int("Номер заказа: ")
        return self._service.find_order(order_id)

    def _print_order(self, order: Order) -> None:
        method = order.delivery_method
        print(f"\n--- Заказ №{order.order_id} [{order.status.value}] ---")
        print(f"Клиент: {order.customer.name}, {order.customer.phone}")
        if method is not None and not method.requires_courier:
            print(f"Пункт выдачи: склад, {self._warehouse.address}")
        else:
            print(f"Адрес доставки: {order.address}")
        print("Позиции:")
        if not order.items:
            print("  корзина пуста")
        for item in order.items:
            print(
                f"  {item.name} × {item.quantity} по {item.price:.2f} = "
                f"{item.total():.2f} руб."
            )
        print(f"Товары: {order.items_cost():.2f} руб.")
        if method is None:
            print("Доставка: не выбрана")
        else:
            print(
                f"Доставка: {method.name}, {order.delivery_cost():.2f} руб., "
                f"срок — {method.estimate_time()}"
            )
            if method.requires_courier:
                courier = order.courier
                print(f"Курьер: {courier.name if courier else 'не назначен'}")
        print(f"Итого: {order.total_cost():.2f} руб.")

    @staticmethod
    def _read_text(prompt: str) -> str:
        """Читает непустую строку, переспрашивая при пустом вводе."""
        while True:
            text = input(prompt).strip()
            if text:
                return text
            print("Значение не может быть пустым.")

    @staticmethod
    def _read_int(prompt: str) -> int:
        """Читает целое число, переспрашивая при неверном формате."""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Введите целое число.")

    @staticmethod
    def _read_float(prompt: str) -> float:
        """Читает число (можно с запятой), переспрашивая при неверном формате."""
        while True:
            try:
                return float(input(prompt).replace(",", "."))
            except ValueError:
                print("Введите число, например 1500 или 99.90.")

    def _read_choice(self, prompt: str, count: int) -> int | None:
        """Читает номер из списка 1..count. Возвращает индекс или None при 0."""
        while True:
            number = self._read_int(prompt)
            if number == 0:
                return None
            if 1 <= number <= count:
                return number - 1
            print(f"Введите число от 0 до {count}.")
