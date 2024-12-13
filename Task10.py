import random
import string
import traceback

# Тестова функція (замінити на свою)
def test_function(input_string):
    # Приклад помилки: функція кидає помилку при рядку з цифрою
    if any(char.isdigit() for char in input_string):
        raise ValueError("Input contains digits!")
    return len(input_string)  # Просто повертає довжину рядка для прикладу

# Генерація випадкового рядка
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Fuzz-тестування
def fuzz_testing(function, num_tests=1000):
    log_file = "fuzz_testing_log.txt"
    
    with open(log_file, "w") as log:
        for i in range(num_tests):
            test_input = generate_random_string()
            try:
                # Викликаємо тестовану функцію
                function(test_input)
            except Exception as e:
                # Логування помилки
                error_message = f"Test #{i+1} failed with input '{test_input}': {str(e)}\n"
                log.write(error_message)
                log.write("Traceback:\n")
                log.write("".join(traceback.format_exc()) + "\n")
                log.write("-" * 80 + "\n")
                print(f"Error in test {i+1}: {test_input}")  # Виводимо помилки в консоль
            else:
                print(f"Test {i+1} passed")

# Запуск fuzz-тестування
fuzz_testing(test_function)