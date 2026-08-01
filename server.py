import http.server
import json
import os

class ProrationHandler(http.server.BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(b"Proration Calculator API is live!")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        
        try:
            body = json.loads(post_data.decode('utf-8'))
        except Exception:
            body = {}

        # Extract values from request body
        old_price = float(body.get("old_price", 0))
        new_price = float(body.get("new_price", 0))
        days_remaining = float(body.get("days_remaining", 0))
        days_in_actual_month = float(body.get("days_in_actual_month", 30))
        spec = str(body.get("spec", "v1")).strip()

        price_diff = new_price - old_price

        # Spec v1: always divide by constant 30
        if spec == "v1":
            charge = price_diff * (days_remaining / 30.0)
        # Spec v2: divide by actual days in the billing month
        else:
            divisor = days_in_actual_month if days_in_actual_month > 0 else 30.0
            charge = price_diff * (days_remaining / divisor)

        # Return required JSON response
        response = {
            "charge": charge
        }

        response_bytes = json.dumps(response).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(response_bytes)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server_address = ('0.0.0.0', port)
    httpd = http.server.HTTPServer(server_address, ProrationHandler)
    print(f"Proration server listening on port {port}...")
    httpd.serve_forever()
