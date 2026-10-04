import json
import os
import random
import time
import uuid

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = FastAPI(title="checkout-api")

# --- Metrics (these become your SLIs) ---
CHECKOUT_REQUESTS = Counter(
    "checkout_requests_total",
    "Total checkout requests by outcome",
    ["outcome"],  # "success" or "error"
)
CHECKOUT_LATENCY = Histogram(
    "checkout_request_duration_seconds",
    "Checkout request latency in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)


def log(event: str, **fields):
    """Structured JSON logs: easy to search by request_id or reason."""
    print(json.dumps({"ts": time.time(), "event": event, **fields}), flush=True)


@app.get("/healthz")
def healthz():
    # Liveness: "is the process alive?"
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    # Readiness: "should this pod receive traffic right now?"
    if os.getenv("DEPENDENCY_DOWN", "false").lower() == "true":
        return JSONResponse(status_code=503, content={"status": "dependency down"})
    return {"status": "ready"}


@app.post("/checkout")
def checkout():
    request_id = str(uuid.uuid4())
    start = time.perf_counter()

    # Fault controls, read on each request
    latency_ms = int(os.getenv("INJECT_LATENCY_MS", "0"))
    error_rate = float(os.getenv("INJECT_ERROR_RATE", "0"))

    if latency_ms > 0:
        time.sleep(latency_ms / 1000)

    if random.random() < error_rate:
        CHECKOUT_REQUESTS.labels(outcome="error").inc()
        CHECKOUT_LATENCY.observe(time.perf_counter() - start)
        log("checkout", request_id=request_id, outcome="error",
            reason="injected_error")
        return JSONResponse(
            status_code=500,
            content={"request_id": request_id, "error": "checkout failed"},
        )

    CHECKOUT_REQUESTS.labels(outcome="success").inc()
    CHECKOUT_LATENCY.observe(time.perf_counter() - start)
    log("checkout", request_id=request_id, outcome="success", reason=None)
    return {"request_id": request_id, "status": "confirmed"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)