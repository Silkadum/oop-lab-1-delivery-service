"""Курьер службы доставки."""


class Courier:
    """Курьер: номер, имя, телефон и признак занятости.

    Один курьер одновременно ведёт не больше одного заказа.
    """

    def __init__(self, courier_id: int, name: str, phone: str) -> None:
        name = name.strip()
        phone = phone.strip()
        if courier_id <= 0:
            raise ValueError("Номер курьера должен быть положительным")
        if not name:
            raise ValueError("Имя курьера не может быть пустым")
        if not phone:
            raise ValueError("Телефон курьера не может быть пустым")
        self.__courier_id = courier_id
        self.__name = name
        self.__phone = phone
        self.__is_free = True

    @property
    def courier_id(self) -> int:
        return self.__courier_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone(self) -> str:
        return self.__phone

    @property
    def is_free(self) -> bool:
        return self.__is_free

    def take_order(self) -> None:
        """Отмечает курьера занятым. Занятого курьера назначить нельзя."""
        if not self.__is_free:
            raise ValueError(f"Курьер {self.__name} уже занят другим заказом")
        self.__is_free = False

    def release(self) -> None:
        """Освобождает курьера после завершения или отмены заказа."""
        self.__is_free = True
