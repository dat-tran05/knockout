"""
HTTP server that receives live sensor data pushed from the Sensor Logger app.
  POST /push   - receive sensor payloads from the app
  GET  /stats  - request counts and most recent packet per sensor
"""

import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
PORT = 8080

_lock = threading.Lock()

# Running totals
stats = {
    "total_requests": 0,
    "total_readings": 0,
    # sensor name → {"count": int, "last_t": float, "last_values": dict}
    "sensors": {},
    # list of {"messageId", "sessionId", "deviceId", "readings", "received_at"}
    "requests": [],
}


class SensorHandler(BaseHTTPRequestHandler):

    # ---- POST /push --------------------------------------------------------
    def do_POST(self):
        if self.path != "/push":
            self._send(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
            self._ingest(data)
            self._send(200)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse: {e}\n[RAW] {raw!r}")
            self._send(400)

    # ---- GET /stats --------------------------------------------------------
    def do_GET(self):
        if self.path != "/stats":
            self._send(404)
            return

        with _lock:
            snapshot = {
                "total_requests": stats["total_requests"],
                "total_readings": stats["total_readings"],
                "sensors": {
                    name: {
                        "count": s["count"],
                        "last_t": s["last_t"],
                        "last_values": s["last_values"],
                    }
                    for name, s in stats["sensors"].items()
                },
                "requests": list(stats["requests"]),
            }

        body = json.dumps(snapshot, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    # ---- helpers -----------------------------------------------------------
    def _send(self, code: int):
        self.send_response(code)
        self.end_headers()

    def _ingest(self, data: dict):
        payload = data.get("payload", [])
        msg_id  = data.get("messageId", "?")
        session = data.get("sessionId", "?")
        device  = data.get("deviceId", "?")
        received_at = datetime.now(timezone.utc).isoformat()

        with _lock:
            stats["total_requests"] += 1
            stats["total_readings"] += len(payload)
            stats["requests"].append({
                "messageId":   msg_id,
                "sessionId":   session,
                "deviceId":    device,
                "readings":    len(payload),
                "received_at": received_at,
            })

            for reading in payload:
                name   = reading.get("name", "unknown")
                ts_ns  = reading.get("time", 0)
                t      = ts_ns / 1_000_000_000
                values = reading.get("values") or {
                    k: v for k, v in reading.items()
                    if k not in ("name", "time", "accuracy")
                }
                accuracy = reading.get("accuracy")

                if name not in stats["sensors"]:
                    stats["sensors"][name] = {"count": 0, "last_t": None, "last_values": None}
                stats["sensors"][name]["count"]       += 1
                stats["sensors"][name]["last_t"]       = t
                stats["sensors"][name]["last_values"]  = values

    def log_message(self, fmt, *args):
        pass  # silence default request logs


# ---------------------------------------------------------------------------
def main():
    import socket
    server = HTTPServer((HOST, PORT), SensorHandler)
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        local_ip = "127.0.0.1"

    print(f"Sensor Logger server  →  port {PORT}")
    print(f"  Push URL  :  http://{local_ip}:{PORT}/push")
    print(f"  Stats     :  http://{local_ip}:{PORT}/stats")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
