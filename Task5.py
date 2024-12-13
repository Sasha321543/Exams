import json
import jwt
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import webbrowser
import sys
import os

# Ігнорування GTK попереджень через перенаправлення stderr
sys.stderr = open(os.devnull, 'w')

# Секретний ключ для підписання JWT
SECRET_KEY = "your_secret_key"

# Створення "бази даних" користувачів
users = {
    "user1": "password123",
    "user2": "mypassword"
}

# Генерація JWT токену
def generate_jwt(username):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Термін дії токену 1 година
    payload = {
        "username": username,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Обробник запитів
class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(message).encode('utf-8'))

    # Обробка запиту для входу
    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            username = data.get("username")
            password = data.get("password")

            # Перевірка коректності логіну та паролю
            if users.get(username) == password:
                token = generate_jwt(username)
                self._send_response(200, {"token": token})
            else:
                self._send_response(401, {"message": "Invalid credentials"})

    # Обробка запиту для захищеного ресурсу
    def do_GET(self):
        if self.path == "/protected":
            token = self.headers.get("Authorization")

            if not token:
                self._send_response(403, {"message": "Token is missing"})
                return

            try:
                token = token.replace("Bearer ", "")  # Видалення "Bearer " з токену
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                self._send_response(200, {"message": f"Welcome, {payload['username']}!"})
            except jwt.ExpiredSignatureError:
                self._send_response(401, {"message": "Token has expired"})
            except jwt.InvalidTokenError:
                self._send_response(401, {"message": "Invalid token"})

# Функція для запуску сервера
def run_server():
    port = 5000
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)  # Автоматичне відкриття сайту в браузері
    print(f"Server is running at {url}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()