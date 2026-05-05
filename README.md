# DevSecOps Pipeline — Fintech PCI DSS Compliance

> **Production-grade DevSecOps pipeline where security scanning, infrastructure provisioning, and compliance enforcement are integrated at every stage of the software delivery lifecycle.**

**Team Lead / Developer 1:** Mehwish Saleem  
**Live API:** `http://16.170.208.184:5000/health`  
**GitHub:** `https://github.com/mehwishsaleem604/devsecops-fintech`  
**Cloud:** AWS EC2 (eu-north-1) | **Registry:** Amazon ECR  

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Team & Roles](#team--roles)
3. [Pipeline Architecture](#pipeline-architecture)
4. [Technology Stack](#technology-stack)
5. [Repository Structure](#repository-structure)
6. [How to Run Locally](#how-to-run-locally)
7. [How to Run the Full Pipeline](#how-to-run-the-full-pipeline)
8. [API Endpoints](#api-endpoints)
9. [Security Vulnerabilities Demo](#security-vulnerabilities-demo)
10. [PCI DSS Compliance Mapping](#pci-dss-compliance-mapping)
11. [AWS Infrastructure](#aws-infrastructure)
12. [Monitoring & Observability](#monitoring--observability)

---

## Project Overview

Traditional development pipelines treat security as a final gate — vulnerabilities are discovered late, compliance checks are performed manually, and infrastructure is configured by hand. This project eliminates those gaps by building a fully automated DevSecOps pipeline for a sample fintech web application.

**No code reaches production unless it passes every security and compliance check.**

The pipeline integrates static code analysis via SonarQube, secret detection via GitLeaks, container vulnerability scanning via Trivy, dynamic attack simulation via OWASP ZAP, PCI DSS compliance validation via OPA Rego policies, cloud infrastructure on AWS EC2, and real-time metrics via Prometheus and Grafana — all triggered automatically on every code push to GitHub.

---

## Team & Roles

| Developer | Role | Responsibilities |
|---|---|---|
| Mehwish Saleem (Dev 1) | DevOps Engineer | GitHub repo, Docker, GitHub Actions pipeline, AWS deployment, README |
| Developer 2 | Security Engineer | SonarQube, GitLeaks, Trivy, OWASP ZAP, vulnerable demo app |
| Developer 3 | Compliance Lead | OPA policies, PCI DSS mapping, Grafana dashboard, pitch slides |
| Developer 4 | Infra & Monitoring Engineer | Terraform IaC, Prometheus, Grafana cost panel |

---

## Pipeline Architecture

Every code push to `main` triggers the following 8 stages in sequence. Any stage failure halts the pipeline and blocks deployment.
Code Push (GitHub)
|
v
Stage 2 — Build & Test

Python 3.11 setup
pip install dependencies
pytest with coverage report
Docker multi-stage build
Image saved as artifact
|
v
Stages 3-5 — Security Scans
SonarQube SAST analysis
GitLeaks secret detection
Trivy container CVE scan
|
v
Stage 5.5 — DAST & ECR Push
OWASP ZAP baseline scan
AWS ECR login
Docker image push to registry
|
v
Stage 6 — Terraform IaC
terraform init
terraform plan
|
v
Stage 7 — PCI DSS Compliance
OPA policy evaluation
Compliance report generated
|
v
Stage 8 — AWS Deploy
SSH into EC2
Pull latest image from ECR
Run container with gunicorn
|
v
Live on AWS EC2
http://16.170.208.184:5000


---

## Technology Stack

| Category | Tool | Version |
|---|---|---|
| Language | Python | 3.11 |
| Framework | Flask | 3.0.3 |
| Database | SQLite | — |
| ORM | SQLAlchemy | 2.0.30 |
| WSGI Server | Gunicorn | 22.0.0 |
| Containerisation | Docker | multi-stage |
| CI/CD | GitHub Actions | — |
| SAST | SonarQube | 10.5 community |
| Secret Detection | GitLeaks | v2 |
| Container Scan | Trivy | latest |
| DAST | OWASP ZAP | 0.12.0 |
| Compliance | Open Policy Agent | Rego |
| Monitoring | Prometheus | 2.52.0 |
| Visualisation | Grafana | 10.4.3 |
| Cloud | AWS EC2 + ECR | t3.micro |
| IaC | Terraform | v3 |

---

## Repository Structure
devsecops-fintech/
├── .github/
│   └── workflows/
│       └── pipeline.yml          # 8-stage CI/CD pipeline
├── .zap/
│   └── rules.tsv                 # OWASP ZAP scan rules
├── app/
│   ├── config.py                 # App configuration & env vars
│   ├── main.py                   # App factory, db, token_required
│   ├── metrics.py                # Prometheus counters & histograms
│   ├── models.py                 # User & Transaction DB models
│   └── routes/
│       ├── admin.py              # Admin endpoints (intentional vulns)
│       ├── auth.py               # Register & login
│       ├── payments.py           # Transfer & history
│       └── users.py              # User lookup & search (SQLi vuln)
├── monitoring/
│   ├── grafana-datasource.yml    # Grafana Prometheus datasource
│   └── prometheus.yml            # Prometheus scrape config
├── opa-policies/
│   └── pci_dss.rego              # OPA PCI DSS compliance rules
├── tests/
│   └── test_app.py               # pytest test suite
├── .gitignore
├── docker-compose.yml            # Local dev stack
├── Dockerfile                    # Multi-stage production build
├── requirements.txt
└── sonar-project.properties      # SonarQube config

---

## How to Run Locally

### Prerequisites
- Docker Desktop installed and running
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/mehwishsaleem604/devsecops-fintech.git
cd devsecops-fintech

# 2. Start all services
docker-compose up --build

# 3. Services available at:
#    API:        http://localhost:5000
#    Prometheus: http://localhost:9090
#    Grafana:    http://localhost:3000  (admin / admin123)
#    SonarQube:  http://localhost:9000
```

### Initialize the database (first run only)

```bash
docker exec -it fintech-api python3 -c "
from app.main import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
app = create_app(testing=True)
with app.app_context():
    db.create_all()
    users = [
        User(username='alice', password_hash=generate_password_hash('alice123'), email='alice@fintech.io', balance=50000.0, role='admin'),
        User(username='bob', password_hash=generate_password_hash('bob123'), email='bob@fintech.io', balance=25000.0),
        User(username='charlie', password_hash=generate_password_hash('charlie123'), email='charlie@fintech.io', balance=15000.0),
    ]
    db.session.bulk_save_objects(users)
    db.session.commit()
    print('Seeded!')
"
```

### Run tests

```bash
pip install -r requirements.txt
pytest tests/ --cov=app --cov-report=xml -v
```

---

## How to Run the Full Pipeline

1. Push any code change to the `main` branch
2. Go to **GitHub → Actions** to watch the pipeline run
3. All 8 stages execute automatically
4. On success, the app deploys to AWS EC2 automatically

To trigger a pipeline run manually:

```bash
git commit --allow-empty -m "trigger pipeline"
git push origin main
```

---

## API Endpoints

Base URL (production): `http://16.170.208.184:5000`

### Authentication

```bash
# Register new user
POST /api/v1/auth/register
Content-Type: application/json
{"username": "testuser", "password": "testpass123", "email": "test@fintech.io"}

# Login
POST /api/v1/auth/login
Content-Type: application/json
{"username": "alice", "password": "alice123"}
# Returns: {"token": "eyJ...", "user_id": 1}
```

### Payments (JWT token required)

```bash

POST /api/v1/payments/transfer
Authorization: Bearer <token>
{"receiver_id": 2, "amount": 100.0, "card_number": "4111111111111111", "cvv": "123"}

# Payment history
GET /api/v1/payments/history/<user_id>
Authorization: Bearer <token>
```

### Infrastructure

```bash
GET /health    # {"status": "healthy", "service": "fintech-api", "version": "1.0.0"}
GET /metrics   # Prometheus metrics output
```

---

## Security Vulnerabilities Demo

The application contains **intentional vulnerabilities** for demonstration — showing the pipeline catching them before production.

| ID | Endpoint | Vulnerability | PCI DSS Req |
|---|---|---|---|
| V1 | `/api/v1/users/search?q=` | SQL Injection | REQ-6.5.1 |
| V4 | `/api/v1/users/<id>` | IDOR — no ownership check | REQ-6.5 |
| V5 | `/api/v1/auth/login` | No rate limiting | REQ-8.2 |
| V6 | `/api/v1/auth/login` | Password logged in plaintext | REQ-2.2 |
| V6 | `/api/v1/payments/transfer` | CVV logged and stored | REQ-3.3 |
| V7 | `/api/v1/admin/report` | Command injection | REQ-6.5.1 |
| V8 | `/api/v1/admin/restore` | Insecure deserialization | REQ-6.5 |

---

## PCI DSS Compliance Mapping

| OPA Policy Rule | PCI DSS Requirement | What It Checks |
|---|---|---|
| `sast_passed` | REQ-6.3 | SonarQube found no critical issues |
| `secret_scan_passed` | REQ-2.2 | No hardcoded credentials in commits |
| `container_scan_passed` | REQ-6.3 | No CRITICAL CVEs in Docker image |
| `dast_passed` | REQ-11.3 | OWASP ZAP found no high-severity issues |
| `tls_enabled` | REQ-4.1 | Encryption in transit enforced |
| `cvv_stored == false` | REQ-3.3 | CVV not stored after authorisation |
| `pan_encrypted` | REQ-3.4 | Card number masked or encrypted |
| `auth_required` | REQ-8.2 | JWT authentication in place |

---

## AWS Infrastructure

| Resource | Details |
|---|---|
| EC2 Instance ID | `i-09cd4bef8e8330ecb` |
| Instance Name | Fintech-Prod-Server |
| Instance Type | t3.micro |
| Public IP | 16.170.208.184 |
| Region | eu-north-1 (Stockholm) |
| ECR Repository | `075433060533.dkr.ecr.eu-north-1.amazonaws.com/fintech-devsecops` |
| Container Port | 5000 |
| OS | Ubuntu 22.04 LTS |

---

## Monitoring & Observability

Prometheus metrics are available live at `http://16.170.208.184:5000/metrics`

| Metric | Type | Description |
|---|---|---|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency per endpoint |
| `payments_processed_total` | Counter | Total payments by status |
| `login_failures_total` | Counter | Total failed login attempts |

To run the full monitoring stack locally with Grafana dashboards:

```bash
docker-compose up -d
# Grafana:    http://localhost:3000  |  admin / admin123
# Prometheus: http://localhost:9090
```

---

*Prepared by Mehwish Saleem — DevOps Engineer | DevSecOps Fintech Project | May 2026*