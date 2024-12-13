import ssl
import socket
import hashlib

def get_certificate_fingerprint(host, port=443):
    # Встановлюємо з’єднання з сервером
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
    conn.connect((host, port))
    
    # Отримуємо сертифікат
    cert = conn.getpeercert(True)
    
    # Зберігаємо сертифікат у файл у форматі DER
    with open(f"{host}_certificate.der", "wb") as cert_file:
        cert_file.write(cert)

    # Перетворюємо сертифікат в формат PEM
    cert_pem = ssl.DER_cert_to_PEM_cert(cert)
    
    # Зберігаємо сертифікат у текстовому форматі (PEM)
    with open(f"{host}_certificate.txt", "w") as cert_txt:
        cert_txt.write(cert_pem)
    
    # Обчислюємо хеш публічного ключа (SHA256)
    public_key_der = ssl.PEM_cert_to_DER_cert(cert_pem)
    hash_object = hashlib.sha256(public_key_der)
    fingerprint = hash_object.hexdigest()

    # Зберігаємо хеш у текстовий файл
    with open(f"{host}_fingerprint.txt", "w") as hash_file:
        hash_file.write(f"SHA-256 Fingerprint: {fingerprint}")
    
    conn.close()

    # Повідомлення про успішне завершення
    print(f"Сертифікат для {host} сформовано та збережено в двох форматах:")
    print(f"1. {host}_certificate.der (DER формат)")
    print(f"2. {host}_certificate.txt (PEM формат)")
    print(f"Хеш публічного ключа збережено в файлі: {host}_fingerprint.txt")

# Приклад використання
host = 'example.com'
get_certificate_fingerprint(host)