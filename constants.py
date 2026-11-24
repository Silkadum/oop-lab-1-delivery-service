"""Константы программы: статусы заказа и тарифы доставки."""

# ----- Статусы заказа -----

STATUS_NEW = "новый"
STATUS_CONFIRMED = "подтверждён"
STATUS_IN_TRANSIT = "в пути"
STATUS_READY_FOR_PICKUP = "готов к выдаче"
STATUS_COMPLETED = "выполнен"
STATUS_CANCELLED = "отменён"

# ----- Тарифы доставки -----

# Стандартная доставка: фиксированная цена, бесплатно от определённой суммы
STANDARD_BASE_COST = 300.0
STANDARD_FREE_FROM = 5000.0

# Экспресс-доставка: базовая цена плюс процент от суммы товаров
EXPRESS_BASE_COST = 500.0
EXPRESS_PERCENT = 0.05

# Самовывоз бесплатный
PICKUP_COST = 0.0
