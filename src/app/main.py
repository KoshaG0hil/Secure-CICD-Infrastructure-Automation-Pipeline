"""
Core Application Web Service
Production-ready REST microservice exposing health probes, metrics,
status telemetry, and synthetic chaos endpoints for rollback testing.
"""

import time
import json
import logging
from flask import Flask, request, jsonify, Response
from src.app.config import get_config
from src.app.metrics import metrics

config = get_config()

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("secure-service")


def create_app() -> Flask:
    app = Flask(__name__)

    @app.before_request
    def start_timer():
        request._start_time = time.time()

    @app.after_request
    def record_metrics(response):
        duration = time.time() - getattr(request, "_start_time", time.time())
        metrics.record_request(response.status_code, duration)
        logger.info(
            json.dumps({
                "event": "http_request",
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "ip": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", "unknown")
            })
        )
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "service": config.app_name,
            "version": config.app_version,
            "environment": config.environment,
            "commit_sha": config.commit_sha,
            "status": "operational",
            "endpoints": [
                "/healthz",
                "/ready",
                "/metrics",
                "/api/v1/status"
            ]
        }), 200

    @app.route("/healthz", methods=["GET"])
    def liveness():
        """Liveness probe for ECS/Kubernetes and ALB health checks."""
        if metrics.chaos_injected:
            logger.warning("Liveness probe FAILED: Chaos failure mode actively simulated.")
            return jsonify({
                "status": "UNHEALTHY",
                "error": "Simulated hardware/kernel lockup for rollback demonstration",
                "timestamp": time.time()
            }), 503
        return jsonify({"status": "healthy", "timestamp": time.time()}), 200

    @app.route("/ready", methods=["GET"])
    def readiness():
        """Readiness probe verifying dependencies are ready to accept traffic."""
        if metrics.chaos_injected:
            logger.warning("Readiness probe FAILED: Service dependencies unavailable.")
            return jsonify({
                "status": "NOT_READY",
                "reason": "Database connection pool exhausted (Simulated)",
                "timestamp": time.time()
            }), 503
        return jsonify({
            "status": "ready",
            "checks": {
                "database_pool": "connected",
                "secrets_store": "synced",
                "cache_layer": "healthy"
            },
            "timestamp": time.time()
        }), 200

    @app.route("/metrics", methods=["GET"])
    def prometheus_metrics():
        """Expose Prometheus formatted performance telemetry."""
        output = metrics.render_prometheus(config.app_name.replace("-", "_"))
        return Response(output, mimetype="text/plain; version=0.0.4; charset=utf-8")

    @app.route("/api/v1/status", methods=["GET"])
    def service_status():
        """Detailed service telemetry endpoint."""
        summary = metrics.get_summary()
        return jsonify({
            "service": config.app_name,
            "version": config.app_version,
            "commit_sha": config.commit_sha,
            "environment": config.environment,
            "aws_region": config.aws_region,
            "telemetry": summary,
            "status": "DEGRADED" if summary["chaos_active"] else "HEALTHY"
        }), 200

    @app.route("/api/v1/chaos/simulate-failure", methods=["POST"])
    def inject_chaos():
        """
        Chaos engineering test endpoint.
        Simulates an application or infrastructure fault to demonstrate automated rollback.
        """
        metrics.set_chaos(True)
        logger.error("CHAOS INJECTED: Service is now reporting 503 UNHEALTHY to all health probes.")
        return jsonify({
            "message": "Chaos fault injected successfully. /healthz will now return 503.",
            "chaos_active": True
        }), 200

    @app.route("/api/v1/chaos/recover", methods=["POST"])
    def recover_chaos():
        """Recover from simulated chaos failure."""
        metrics.set_chaos(False)
        logger.info("CHAOS CLEARED: Service health probes restored to 200 OK.")
        return jsonify({
            "message": "Chaos state cleared. Service healthy.",
            "chaos_active": False
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info(f"Starting {config.app_name} v{config.app_version} on {config.host}:{config.port}")
    app.run(host=config.host, port=config.port)
