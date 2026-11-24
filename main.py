"""Точка входа: создаёт склад, сервис и консольный интерфейс."""

from models.warehouse import Warehouse
from services.order_service import OrderService
from ui.console_ui import ConsoleUI


def main() -> None:
    warehouse = Warehouse("ул. Профессора Попова, 5")
    warehouse.add_product("Клавиатура", 2500, 10)
    warehouse.add_product("Мышь", 1200, 15)
    warehouse.add_product("Монитор", 15000, 3)

    service = OrderService(warehouse)
    service.add_courier("Иван Петров", "+7 900 111-22-33")
    service.add_courier("Катя Смирнова", "+7 900 444-55-66")

    ConsoleUI(service, warehouse).run()


if __name__ == "__main__":
    main()
