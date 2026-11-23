"""Клиент службы доставки."""


class Customer:
    """Клиент, оформивший заказ: имя и телефон."""

    def __init__(self, name: str, phone: str) -> None:
        name = name.strip()
        phone = phone.strip()
        if not name:
            raise ValueError("Имя клиента не может быть пустым")
        if not phone:
            raise ValueError("Телефон клиента не может быть пустым")
        self._name = name
        self._phone = phone

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone
