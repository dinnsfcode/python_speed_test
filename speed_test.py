import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT = 30
MIB = 1024 ** 2


def validate_url(url):
    try:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError("Укажи полный URL, начинающийся с http:// или https://")
        _ = parts.port
    except ValueError as error:
        raise ValueError(f"Некорректный URL: {error}") from error


def measure_speed(url):
    total_bytes = 0
    total_seconds = 0.0

    for number in range(1, REQUEST_COUNT + 1):
        request = Request(url, headers={"Cache-Control": "no-cache"})
        start = time.perf_counter()

        try:
            with urlopen(request, timeout=TIMEOUT) as response:
                downloaded_bytes = 0
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    downloaded_bytes += len(chunk)
        except HTTPError as error:
            raise RuntimeError(f"Запрос {number}: HTTP {error.code} ({error.reason})") from error
        except (URLError, TimeoutError, OSError) as error:
            raise RuntimeError(f"Запрос {number}: ошибка соединения: {error}") from error

        elapsed = time.perf_counter() - start
        total_bytes += downloaded_bytes
        total_seconds += elapsed
        print(f"Запрос {number}: {elapsed:.3f} с | {downloaded_bytes / MIB:.2f} МиБ")

    average_seconds = total_seconds / REQUEST_COUNT
    average_speed = total_bytes / MIB / total_seconds if total_seconds else 0.0

    print("\nРезультаты:")
    print(f"Среднее время запроса: {average_seconds:.3f} с")
    print(f"Всего скачано: {total_bytes / MIB:.2f} МиБ")
    print(f"Средняя скорость: {average_speed:.2f} МиБ/с")


def main():
    if len(sys.argv) != 2:
        print("Использование: python3 speed_test.py <URL>", file=sys.stderr)
        return 1

    try:
        validate_url(sys.argv[1])
        measure_speed(sys.argv[1])
    except (ValueError, RuntimeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
