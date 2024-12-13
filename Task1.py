import hashlib

def hash_message_sha256(message: str) -> str:
    """
    Хешує повідомлення за допомогою алгоритму SHA-256.

    :param message: Рядок, який потрібно хешувати.
    :return: Хеш-значення у шістнадцятковому форматі.
    """
    # Перетворюємо повідомлення на байти
    message_bytes = message.encode('utf-8')
    
    # Створюємо об'єкт SHA-256
    sha256_hash = hashlib.sha256()
    
    # Обчислюємо хеш
    sha256_hash.update(message_bytes)
    
    # Повертаємо хеш у шістнадцятковому форматі
    return sha256_hash.hexdigest()

# Приклад використання
if __name__ == "__main__":
    input_message = input("Введіть повідомлення для хешування: ")
    hash_result = hash_message_sha256(input_message)
    print(f"SHA-256 хеш: {hash_result}")