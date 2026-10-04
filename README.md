# SLO Reliability Lab

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Kubernetes-Ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes" />
  <img src="https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus" />
</p>

<p align="center">
  <strong>Alert on what users experience, not on what servers are doing.</strong>
</p>

A small but practical reliability lab for learning how to define Service Level Indicators (SLIs), Service Level Objectives (SLOs), and operational alerts around user-facing outcomes rather than infrastructure noise.

This project models a checkout API that intentionally exposes controllable latency and failure injection so you can experiment with dashboards, alerting, readiness, liveness, and SLO-based incident response in a realistic, low-friction setup.

## Why this project?

When services are noisy and complex, conventional alerts often fire on CPU, memory, or instance-level health without reflecting the actual experience of end users. This repo flips that approach.

Instead of asking:

- "Are my servers healthy?"

it asks:

- "Are users successfully completing checkout requests?"
- "Is the experience fast enough?"
- "Are we breaching the SLO before the incident gets severe?"

The result is a clear path from service behavior to alerting, dashboards, and operational decisions.

## Architecture

```text
┌─────────────────────┐
│ User / Client       │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│ FastAPI Checkout API │
│ - /checkout         │
│ - /healthz          │
│ - /readyz           │
│ - /metrics          │
└──────────┬──────────┘
           │
           │ Prometheus scrape
           ▼
┌─────────────────────┐
│ Prometheus / Alerting │
│ - error-rate SLO     │
│ - latency SLO        │
│ - readiness alert    │
└─────────────────────┘
```

## Features

- FastAPI-based checkout service with realistic request outcomes
- Injected latency and error simulation via environment variables
- Prometheus-compatible metrics for request counts and latency histograms
- Kubernetes deployment and Service manifests
- ServiceMonitor and PrometheusRule examples for monitoring and alerting
- Simple test suite for health, readiness, checkout, and metrics exposure
- A practical SLO-first operational model

## API behavior

The service exposes a minimal, intentionally understandable API:

- `GET /healthz` — liveness probe
- `GET /readyz` — readiness probe; fails when `DEPENDENCY_DOWN=true`
- `POST /checkout` — simulates a checkout request and returns a success or failure based on injected fault conditions
- `GET /metrics` — exposes Prometheus metrics

### Fault injection

The app reads runtime environment variables:

- `INJECT_LATENCY_MS` — adds artificial latency to a request
- `INJECT_ERROR_RATE` — injects a probability of request failure
- `DEPENDENCY_DOWN` — forces readiness failure for demonstration purposes

This makes it easy to test incident conditions without changing code.

## Observability and SLOs

The repository includes a Prometheus-based observability stack:

- `observability/servicemonitor.yaml` — scrapes `/metrics`
- `observability/alert-rules.yaml` — defines SLO alerting rules
- `observability/checkout-dashboard.json` — dashboard with operational visibility
- `observability/kps-values.yaml` — values for the monitoring stack configuration

The alert rules cover:

- `CheckoutHighErrorRate` — error rate above 2% for 5 minutes
- `CheckoutHighLatencyP95` — p95 latency above 500ms for 10 minutes
- `CheckoutNotReady` — pod readiness failure over a short threshold

## Quick start

### 1) Run locally

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then visit:

- `http://localhost:8000/healthz`
- `http://localhost:8000/readyz`
- `http://localhost:8000/metrics`

### 2) Test the application

```bash
cd app
pytest -q
```

### 3) Build the container

```bash
docker build -t checkout-api:0.1.0 .
```

### 4) Deploy on Kubernetes

```bash
kubectl apply -f k8s/
```

The deployment includes health probes and environment controls for reliability testing.

## Project structure

```text
.
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── test_api.py
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── observability/
│   ├── alert-rules.yaml
│   ├── checkout-dashboard.json
│   ├── kps-values.yaml
│   └── servicemonitor.yaml
├── Dockerfile
├── .gitignore
└── README.md
```

## Example metrics

The app exports Prometheus metrics such as:

- `checkout_requests_total{outcome="success|error"}`
- `checkout_request_duration_seconds_bucket`
- `checkout_request_duration_seconds_count`
- `checkout_request_duration_seconds_sum`

These are the foundation of the SLI and alerting work in this lab.

## Learning goals

This project is useful for exploring:

- SLI/SLO definition
- user-centered alerting
- Prometheus metric design
- readiness and liveness patterns
- reliability testing in a Kubernetes environment
- incident response based on customer impact rather than host-level symptoms

## Contributing

This repo is intentionally small and educational. Contributions that improve the reliability model, observability configuration, or documentation are welcome.

## License

This project is provided for learning and experimentation. Add an appropriate license if you plan to reuse or distribute it in production or shared environments.

---

<p align="center">
  <strong>Built for learning reliability engineering the way users actually experience it.</strong>
</p>
