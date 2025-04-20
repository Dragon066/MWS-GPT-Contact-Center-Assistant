import random


def generate_phone():
    prefixes = ["916", "915", "925", "928", "903", "905", "999"]
    return f"8-{random.choice(prefixes)}-{random.randint(100, 999):03d}-{random.randint(10, 99):02d}-{random.randint(10, 99):02d}"


def generate_tariff(is_mts):
    if not is_mts:
        return "?"
    return random.choice(
        [
            "Конвергентный тарифный план Тариф №7 (мобильная связь МТС + домашний интернет + ТВ)",
            "Архивный тариф Smart 122021",
            "Тариф «Для своих»",
            "Твой безлимит 2.0",
            "ULTRA",
            "Smart Безлимит",
        ]
    )


def generate_device():
    devices = [
        ("iPhone 16 pro 256 GB", "iOS", ["18.4", "17.2", "16.5"]),
        ("Samsung S22 512GB", "Android", ["15", "14", "13"]),
        ("Desktop, dell", "Windows", ["10", "11"]),
        ("Xiaomi Redmi Note 13", "Android", ["14", "13"]),
        ("Google Pixel 8", "Android", ["15"]),
        ("Huawei P60", "HarmonyOS", ["3.0", "2.1"]),
    ]
    device, os, versions = random.choice(devices)
    return device, f"{os}, версия {random.choice(versions)}"


def generate_services():
    services = [
        "Чёрный список - 1,5 руб/день",
        "Вам звонили - 1,3 руб/день",
        "Антивирус PRO - 2 руб/день",
        "Погода Premium - 1 руб/день",
        "Детский интернет - 3 руб/день",
    ]
    if random.random() < 0.3:
        return "да:\n • " + "\n • ".join(
            random.sample(services, k=random.randint(1, 2))
        )
    return "нет"


def generate_subscriber():
    is_mts = random.random() < 0.7
    device, os = generate_device()
    has_app_mts = random.choice([True, False]) if is_mts else False
    has_mts_bank = random.choice([True, False])

    return {
        "Номер телефона": generate_phone(),
        "Абонент МТС": "да" if is_mts else "нет",
        "Тариф": generate_tariff(is_mts),
        "Мобильная связь": random.choice(["есть", "нет"]),
        "Домашний интернет": random.choice(["есть", "нет"]),
        "Домашнее ТВ": random.choice(["есть", "нет"]),
        "Домашний телефон": random.choice(["есть", "нет"]),
        "Устройство": device,
        "ОС": os,
        "Пользователь приложения Мой МТС": "да" if has_app_mts else "нет",
        "Пользователь Личный кабинет": random.choice(["да", "нет"]),
        "Пользователь приложения МТС Банк": "да" if has_mts_bank else "нет",
        "Пользователь приложения МТС Деньги": random.choice(["да", "нет"]),
        "Подписки и сервисы на номере": generate_services(),
        "МТС Premium": random.choice(["есть", "нет"]),
        "МТС Cashback": random.choice(["есть", "нет"]),
        "Защитник базовый": random.choice(["есть", "нет"]),
        "Защитник+": random.choice(["есть", "нет"]),
        "Отдельная подписка Kion": random.choice(["есть", "нет"]),
        "Отдельная подписка Музыка": random.choice(["есть", "нет"]),
        "Отдельная подписка Строки": random.choice(["есть", "нет"]),
        "Дебетовая карта МТС Банк": "да"
        if has_mts_bank and random.random() < 0.5
        else "нет",
        "Кредитная карта МТС Банк": random.choice(["да", "нет"]),
        "Дебетовая карта МТС Деньги": random.choice(["да", "нет"]),
        "Кредитная карта МТС Деньги": random.choice(["да", "нет"]),
        "Виртуальная карта МТС Деньги": random.choice(["да", "нет"]),
    }
