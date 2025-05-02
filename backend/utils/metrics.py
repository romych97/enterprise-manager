from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from typing import Callable
from functools import wraps

# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

# Business metrics
CLIENT_COUNT = Gauge("clients_total", "Total number of clients")

ORDER_COUNT = Gauge("orders_total", "Total number of orders", ["status"])

TASK_COUNT = Gauge("tasks_total", "Total number of tasks", ["status"])


def track_request_latency(method: str, endpoint: str):
    """Decorator to track request latency"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                response = await func(*args, **kwargs)
                REQUEST_COUNT.labels(
                    method=method, endpoint=endpoint, status="success"
                ).inc()
                return response
            except Exception as e:
                REQUEST_COUNT.labels(
                    method=method, endpoint=endpoint, status="error"
                ).inc()
                raise e
            finally:
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(
                    time.time() - start_time
                )

        return wrapper

    return decorator


def start_metrics_server(port: int = 8000):
    """Start the Prometheus metrics server"""
    start_http_server(port)
