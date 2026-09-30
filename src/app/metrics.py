"""
Metrics Collector Module
Maintains in-memory application performance and reliability counters,
formatting them into Prometheus standard text format.
"""

import time
import threading
from typing import Dict


class MetricsRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self.request_count: int = 0
        self.error_count: int = 0
        self.status_codes: Dict[int, int] = {}
        self.start_time: float = time.time()
        self.chaos_injected: bool = False

    def record_request(self, status_code: int, duration_sec: float):
        with self._lock:
            self.request_count += 1
            self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
            if status_code >= 500:
                self.error_count += 1

    def set_chaos(self, active: bool):
        with self._lock:
            self.chaos_injected = active

    def get_summary(self) -> Dict:
        with self._lock:
            uptime = time.time() - self.start_time
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0
            return {
                "uptime_seconds": round(uptime, 2),
                "total_requests": self.request_count,
                "error_count": self.error_count,
                "error_rate_pct": round(error_rate, 2),
                "status_codes": dict(self.status_codes),
                "chaos_active": self.chaos_injected
            }

    def render_prometheus(self, app_name: str) -> str:
        summary = self.get_summary()
        lines = [
            f"# HELP {app_name}_http_requests_total Total number of HTTP requests processed",
            f"# TYPE {app_name}_http_requests_total counter",
            f'{app_name}_http_requests_total {summary["total_requests"]}',
            f"# HELP {app_name}_http_errors_total Total number of 5xx HTTP server errors",
            f"# TYPE {app_name}_http_errors_total counter",
            f'{app_name}_http_errors_total {summary["error_count"]}',
            f"# HELP {app_name}_uptime_seconds Total runtime of the service in seconds",
            f"# TYPE {app_name}_uptime_seconds gauge",
            f'{app_name}_uptime_seconds {summary["uptime_seconds"]}',
            f"# HELP {app_name}_chaos_active Status of chaos test mode (1 active, 0 normal)",
            f"# TYPE {app_name}_chaos_active gauge",
            f'{app_name}_chaos_active {1 if summary["chaos_active"] else 0}'
        ]
        for code, count in summary["status_codes"].items():
            lines.append(f'{app_name}_http_status_codes{{status="{code}"}} {count}')
        return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
