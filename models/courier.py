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
        self._courier_id = courier_id
        self._name = name
        self._phone = phone
        self._is_free = True

    @property
    def courier_id(self) -> int:
        return self._courier_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def is_free(self) -> bool:
        return self._is_free

    def take_order(self) -> None:
        """Отмечает курьера занятым. Занятого курьера назначить нельзя."""
        if not self._is_free:
            raise ValueError(f"Курьер {self._name} уже занят другим заказом")
        self._is_free = False

    def release(self) -> None:
        """Освобождает курьера после завершения или отмены заказа."""
        self._is_free = True
