from prometheus_client import Counter, Histogram, Gauge, start_http_server

class MetricsExporter:
    def __init__(self, port: int = 9090):
        # Define metrics
        self.request_counter = Counter(
            'safety_requests_total', 
            'Total number of safety validation requests', 
            ['status']
        )
        self.violation_counter = Counter(
            'safety_violations_total', 
            'Total number of safety violations', 
            ['type']
        )
        self.latency_histogram = Histogram(
            'safety_validation_latency_seconds', 
            'Time taken for safety checks'
        )
        self.safety_score_gauge = Gauge(
            'safety_score_current',
            'Current safety score of the system'
        )
        
        # Start server if needed (FastAPI usually handles this via /metrics endpoint middleware)
        # But for standalone exporter:
        # start_http_server(port)

    def record_request(self, status: str):
        self.request_counter.labels(status=status).inc()

    def record_violation(self, type: str):
        self.violation_counter.labels(type=type).inc()

    def record_latency(self, seconds: float):
        self.latency_histogram.observe(seconds)

    def update_safety_score(self, score: float):
        self.safety_score_gauge.set(score)
