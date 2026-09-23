"""Проверка работы FkkoClient: делаем один запрос и смотрим ответ."""

import sys

sys.path.insert(0, "src")

from http_client import FkkoClient  # noqa: E402


def main() -> None:
    client = FkkoClient()
    response = client.get("/fkko/")

    if response is None:
        print("Запрос не удался. Смотри логи выше.")
        return

    print(f"Статус: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Размер ответа: {len(response.text)} символов")
    print()
    print("Первые 500 символов ответа:")
    print("-" * 60)
    print(response.text[:500])


if __name__ == "__main__":
    main()