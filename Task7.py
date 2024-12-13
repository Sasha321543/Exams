import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Функція для перевірки на наявність шкідливих символів
def detect_sql_injection(input_data):
    # Список небезпечних патернів для SQL-ін'єкцій
    sql_keywords = [
        r"union.*select", r"select.*from", r"drop.*table", r"insert.*into",
        r"update.*set", r"delete.*from", r"select.*where", r" --", r" #",
        r"/*", r"*/", r"or.*1=1", r"and.*1=1", r"execute", r"xp_"
    ]
    
    for keyword in sql_keywords:
        if re.search(keyword, input_data, re.IGNORECASE):
            return True
    return False

# Клас для обробки запитів
class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Відправка HTML-форм для введення даних
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        self.wfile.write("""
        <html>
        <head>
        <meta charset="UTF-8">
        </head>
            <body>
            <h1>Введіть дані:</h1>
            <form method="POST">
            <input type="text" name="user_input" />
            <input type="submit" value="Надіслати" />
            </form>
                <p>Дозволено вводити текст, але не використовуйте SQL-оператори або спеціальні символи (наприклад, `--`, `;`, `DROP` і т.д.).</p>
            </body>
            </html>
            """.encode('utf-8'))
    def do_POST(self):
        # Отримання введених даних з форми
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        post_data = parse_qs(post_data)
        user_input = post_data.get('user_input', [''])[0]
        
        # Перевірка на наявність SQL-ін'єкцій
        if detect_sql_injection(user_input):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <html>
                <head>
                <meta charset="UTF-8">
                </head>
                <body>
                    <h1>Попередження!</h1>
                    <p>Виявлено спробу SQL-ін’єкції: {user_input}</p>
                    <a href="/">Повернутись назад</a>
                </body>
            </html>
            """.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <html>
                <head>
                <meta charset="UTF-8">
                </head>
                <body>
                    <h1>Дані прийнято успішно!</h1>
                    <p>Ви ввели: {user_input}</p>
                    <a href="/">Повернутись назад</a>
                </body>
            </html>
            """.encode('utf-8'))

# Налаштування сервера
def run():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, MyHandler)
    print('Server started on port 8080...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()