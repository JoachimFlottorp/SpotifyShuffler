from http.server import HTTPServer, BaseHTTPRequestHandler

token = ""

class S(BaseHTTPRequestHandler):
    def do_GET(self):
        global token
        if self.path[5:] == "error":
            token = "ACCESS_DENIED CAN NOT GET TOKEN"
        else:
            token = self.path[7:]
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes(f"<p>Gotten access token: {token} <br><br>Now asking spotify for authorization code! You can return to your terminal..</p>", "utf-8"))
    
    def log_message(self, format: str, *args) -> None:
        # Disable logging
        return
        

def server_forever(httpd):
    # Hey, i only need one request :)
    while 1:
        httpd.handle_request()
        break

def run():
    server_address = ('127.0.0.1', 5273)
    httpd = HTTPServer(server_address, S)
    server_forever(httpd)
    return token