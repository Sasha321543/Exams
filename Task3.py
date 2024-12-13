import socket
from datetime import datetime
import threading
from queue import Queue
import sys
import signal

# Функція для обробки сигналу переривання
def signal_handler(sig, frame):
    print("\nСканування перервано користувачем.")
    sys.exit(0)

# Реєструємо обробку Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Функція для сканування порту
def scan_port(host, port, open_ports):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                open_ports.append(port)
    except Exception as e:
        pass

# Функція для оновлення прогресу
def print_progress(total, current):
    progress = int((current / total) * 50)  # Шкала прогресу з 50 символів
    bar = "=" * progress + "." * (50 - progress)
    print(f"\r[{bar}] {current}/{total} портів перевірено", end="")

# Основна функція
def port_scanner():
    # Визначення хоста
    host = socket.gethostname()
    host_ip = socket.gethostbyname(host)

    # Визначення діапазону портів
    start_port = 1
    end_port = 1024

    print(f"\nЗапуск сканування хоста: {host_ip}")
    print(f"Діапазон портів: {start_port}-{end_port}")
    print("Натисніть Ctrl+C для завершення сканування вручну.\n")

    # Час початку
    start_time = datetime.now()

    # Змінна для зберігання відкритих портів
    open_ports = []

    # Створення черги для багатопоточності
    queue = Queue()
    for port in range(start_port, end_port + 1):
        queue.put(port)

    # Функція для роботи потоку
    def worker():
        while not queue.empty():
            port = queue.get()
            scan_port(host_ip, port, open_ports)
            nonlocal checked_ports
            checked_ports += 1
            print_progress(total_ports, checked_ports)

    # Ініціалізація прогресу
    total_ports = end_port - start_port + 1
    checked_ports = 0

    # Запуск потоків
    threads = []
    for _ in range(100):  # 100 потоків
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Час завершення
    end_time = datetime.now()
    duration = end_time - start_time

    # Виведення результатів
    print("\nСканування завершено.")
    print(f"Відкриті порти ({len(open_ports)}): {', '.join(map(str, open_ports)) if open_ports else 'Немає відкритих портів.'}")
    print(f"Час виконання: {duration}")

    # Запис результатів у файл
    with open("scan_results.txt", "w") as file:
        file.write(f"Хост: {host_ip}\n")
        file.write(f"Діапазон портів: {start_port}-{end_port}\n")
        file.write(f"Час виконання: {duration}\n")
        file.write(f"Відкриті порти ({len(open_ports)}): {', '.join(map(str, open_ports)) if open_ports else 'Немає відкритих портів.'}\n")

    print("\nРезультати записані у файл 'scan_results.txt'.")

# Запуск програми
if __name__ == "__main__":
    port_scanner()