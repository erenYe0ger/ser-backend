# ser-backend

Production-grade FastAPI backend powering a Speech Emotion Recognition (SER) system, built as a portfolio project demonstrating scalable backend engineering practices for modern distributed applications.

## Live Demo

Frontend: https://ser-frontend-eight.vercel.app

---

## Architecture Overview

```text
React Frontend (Vercel)
            |
            v
FastAPI Backend (Render)
            |
            v
     SHA-256 Hash
            |
            v
 Redis Cache (Upstash)
      |          |
   HIT|          |MISS
      |          v
      |   HuggingFace Spaces
      |      Inference API
      |          |
      |          v
      |   PostgreSQL (Neon)
      |          |
      +----------+
            |
            v
      JSON Response
```

### Request Flow

1. React frontend uploads an audio file to the FastAPI backend.
2. Backend computes a SHA-256 hash of the audio contents.
3. Redis (Upstash) is checked for a cached prediction.
4. On cache hit:

   * Return cached prediction immediately.
5. On cache miss:

   * Forward audio to the HuggingFace Spaces inference API.
   * Receive emotion prediction results.
   * Persist prediction metadata in PostgreSQL (Neon.tech).
   * Cache the result in Redis.
6. Return:

```json
{
  "emotion": "happy",
  "confidence": 0.91,
  "all_emotions": {
    "happy": 0.91,
    "neutral": 0.05,
    "sad": 0.04
  },
  "source": "model"
}
```

---

## Tech Stack

| Technology             | Purpose                        |
| ---------------------- | ------------------------------ |
| FastAPI                | High-performance API framework |
| SQLAlchemy (Async)     | ORM and database access        |
| asyncpg                | PostgreSQL async driver        |
| PostgreSQL (Neon.tech) | Persistent storage             |
| Redis (Upstash)        | Distributed caching            |
| httpx                  | Async HTTP client              |
| pydantic-settings      | Environment configuration      |
| Docker                 | Containerization               |
| Render                 | Backend deployment platform    |

---

## Key Engineering Decisions

### HuggingFace Spaces for Inference

* Speech emotion models are memory intensive.
* Render free and starter instances have limited RAM.
* Offloading inference to HuggingFace Spaces keeps the API lightweight and scalable while separating concerns between serving and inference.

### Async SQLAlchemy

* Uses SQLAlchemy 2.x async APIs with asyncpg.
* Prevents blocking the FastAPI event loop during database operations.
* Improves throughput under concurrent request load.

### SHA-256 Content Addressable Caching

* Cache key is derived from file contents rather than filename.
* Identical audio files always produce the same cache key.
* Eliminates duplicate inference requests and reduces latency.

### Conditional SSL for Neon.tech

* Neon PostgreSQL requires SSL in production.
* Backend supports conditional asyncpg SSL configuration to work in both local Docker environments and managed cloud deployments.

### Docker Healthchecks

* Prevents application startup before PostgreSQL becomes ready.
* Eliminates common container startup race conditions.
* Improves reliability during local development and deployment.

---

## API Endpoints

| Method | Endpoint          | Description                                 |
| ------ | ----------------- | ------------------------------------------- |
| POST   | `/api/v1/predict` | Upload audio and receive emotion prediction |
| GET    | `/api/v1/history` | Retrieve recent prediction history          |

### POST /api/v1/predict

Accepts:

* Multipart audio file upload

Returns:

```json
{
  "emotion": "happy",
  "confidence": 0.91,
  "all_emotions": {
    "happy": 0.91,
    "neutral": 0.05,
    "sad": 0.04
  },
  "source": "cache"
}
```

### GET /api/v1/history

Returns recent prediction records:

```json
[
  {
    "id": 1,
    "audio_filename": "sample.wav",
    "emotion": "happy",
    "confidence": 0.91,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

---

## Local Development

### Clone Repository

```bash
git clone https://github.com/erenYe0ger/ser-backend.git
cd ser-backend
```

### Create .env

```env
DATABASE_URL=postgresql+asyncpg://ser_user:ser_password@postgres:5432/ser_db
REDIS_URL=redis://redis:6379
HF_SPACES_URL=https://staticgeek-wav2vec2-ser-ravdess.hf.space
APP_NAME=SER Backend
DEBUG=True
```

### Start Services

```bash
docker-compose up --build
```

### API Documentation

```text
http://localhost:8000/docs
```

---

## Environment Variables

| Variable      | Description                           |
| ------------- | ------------------------------------- |
| DATABASE_URL  | PostgreSQL connection string          |
| REDIS_URL     | Redis connection string               |
| HF_SPACES_URL | HuggingFace Spaces inference endpoint |
| APP_NAME      | FastAPI application name              |
| DEBUG         | Enables SQL logging and debug mode    |

---

## Related Repos

### ser-frontend

React frontend responsible for:

* Audio uploads
* Visualization of prediction probabilities
* Viewing prediction history
* Communicating with this backend through REST APIs

Repository:

```text
https://github.com/erenYe0ger/ser-frontend
```
