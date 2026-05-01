
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"],
)
PAYMENT_COUNTER = Counter(
    "payments_processed_total",
    "Total payments processed",
    ["status"],
)
LOGIN_FAILURES = Counter(
    "login_failures_total",
    "Total failed login attempts",
)
