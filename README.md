# Distributed Rate-Limiting and Quota Management Platform

## 🚀 Overview
This project implements a **Distributed Rate-Limiting and Quota Management Platform** designed to handle **2M+ requests per second (RPS)** with **sub-millisecond decision latency**.  
It combines **local in-memory fast-path rate limiting** with **Redis Lua atomic operations** for global accuracy and scalability.

The system ensures accurate throttling, low latency, fault tolerance, and minimal memory usage — making it suitable for large-scale production environments.

---

## ⚙️ Features
✅ Accurate rate limiting using **Token Bucket algorithm**  
✅ Sub-ms latency using **in-memory local buckets**  
✅ Distributed global enforcement via **Redis Lua scripts**  
✅ Fault-tolerant fallback mode when Redis is unavailable  
✅ Rule-based throttling with flexible JSON configuration  
✅ Clear API responses with HTTP `429 Too Many Requests`  
✅ Dockerized and ready for scaling with Kubernetes  

---

## 🧩 Architecture
```
Clients → FastAPI App (RateLimit Middleware) → Redis Cluster (Atomic Lua Script)
                           ↓
              Prometheus / Grafana for metrics
```

### Components
- **FastAPI App**: Main microservice that enforces rate limits.
- **Redis (7.x)**: Shared distributed state using Lua scripting.
- **Lua Script**: Implements atomic token bucket logic for concurrency-safe updates.
- **Local Buckets**: Fast-path in-memory limiter for sub-ms decisions.
- **Rules Engine**: Loads JSON rules defining per-IP, per-route, or per-tenant limits.

---

## 📦 Folder Structure
```
distributed_rate_limiter/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + middleware
│   ├── rate_limiter.py         # Core limiter logic
│   ├── rules.json              # Sample rule configuration
├── lua/
│   └── token_bucket.lua        # Redis Lua script
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🏗️ How It Works
1. Each incoming request triggers a middleware check.
2. The request key (IP, route, tenant) is resolved using a rule.
3. A **local in-memory bucket** is checked first (ultra-fast).
4. If local tokens exhausted, the system calls **Redis Lua script** for atomic check/update.
5. Redis returns whether to allow or deny the request.
6. If Redis is unreachable, the app switches to **fallback local mode**.
7. The app returns `HTTP 429` with `Retry-After` headers when throttled.

---

## 🧪 Running Locally

### Prerequisites
- Python 3.11+
- Docker / Docker Compose

### 1️⃣ Clone & Setup
```bash
git clone <repo_url>
cd distributed_rate_limiter
pip install -r requirements.txt
```

### 2️⃣ Start Redis and App
Using Docker Compose:
```bash
docker-compose up --build
```

App will start at: [http://localhost:8000](http://localhost:8000)

### 3️⃣ Test API
```bash
curl http://localhost:8000/ping
```

### 4️⃣ Load Test
```bash
python load_test.py
```

---

## 🧠 Example Response
When throttled:
```json
HTTP/1.1 429 Too Many Requests
Retry-After: 2
X-RateLimit-Remaining: 0
{
  "detail": "Too Many Requests",
  "retry_after_ms": 2000
}
```

---

## ⚡ Scaling Notes
- Deploy **FastAPI** app replicas behind a load balancer.
- Use **Redis Cluster** (10+ shards) for 2M+ RPS.
- Configure autoscaling via HPA based on CPU and Redis latency.
- Monitor with Prometheus metrics: request rate, latency, 429 rate, Redis RTT.

---

## 🧭 Key Technologies
- **Python** (FastAPI, asyncio)
- **Redis** (Cluster, Lua scripts)
- **Docker / Kubernetes**
- **Prometheus / Grafana** for metrics
- **Token Bucket algorithm** for throttling logic

---

## 📜 License
Open-sourced for educational and architectural demonstration purposes.

---

### 👨‍💻 Author
**Distributed Rate-Limiting System Example by GPT-5**  
Designed for scalability, accuracy, and reliability.
