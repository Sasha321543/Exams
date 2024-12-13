import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json

# Дані користувачів та їхні ролі
users_db = {
    "admin": {"password": "adminpass", "role": "ROLE_ADMIN"},
    "user": {"password": "userpass", "role": "ROLE_USER"}
}

# Сесія користувача
current_user = None

# Перевірка ролей
def role_required(role):
    def decorator(func):
        def wrapper(path, params):
            if current_user is None:
                return "HTTP/1.1 302 Found\r\nLocation: /login\r\n\r\n"
            if users_db[current_user]["role"] != role:
                return "HTTP/1.1 403 Forbidden\r\n\r\nAccess Denied: You do not have the required role"
            return func(path, params)
        return wrapper
    return decorator

# Основна логіка обробки запитів
class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    # Головна сторінка
    def do_GET(self):
        global current_user
        path = self.path
        params = parse_qs(urlparse(self.path).query)
        
        if path == "/":
            if current_user:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"Welcome {current_user}! <a href='/logout'>Logout</a>".encode())
            else:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
        
        elif path == "/login":
            if current_user:
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(self.get_login_form().encode())
        
        elif path == "/logout":
            current_user = None
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
        
        elif path == "/user":
            @role_required("ROLE_USER")
            def user_page(path, params):
                self.send_response(200)
                self.end_headers()
                self.wfile.write("This is the user page.".encode())
            user_page(path, params)
        
        elif path == "/admin":
            @role_required("ROLE_ADMIN")
            def admin_page(path, params):
                self.send_response(200)
                self.end_headers()
                self.wfile.write("This is the admin page.".encode())
            admin_page(path, params)
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write("Page not found".encode())

    # Обробка POST запитів для логіну
    def do_POST(self):
        global current_user
        path = self.path
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode()
        
        params = parse_qs(body)
        if path == "/login":
            username = params.get("username", [""])[0]
            password = params.get("password", [""])[0]
            
            if username in users_db and users_db[username]["password"] == password:
                current_user = username
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(self.get_login_form("Invalid credentials").encode())

    # Форма для логіну
    def get_login_form(self, error_message=""):
        return f'''
        <html>
            <body>
                <h2>Login</h2>
                {f'<p style="color:red;">{error_message}</p>' if error_message else ''}
                <form method="post" action="/login">
                    Username: <input type="text" name="username"><br>
                    Password: <input type="password" name="password"><br>
                    <input type="submit" value="Login">
                </form>
            </body>
        </html>
        '''

# Налаштування серверу
PORT = 8000
Handler = SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    httpd.serve_forever()