# Backend Development Guide

## Virtual Environment Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your YouCam credentials:

```bash
YOUCAM_API_KEY=sk-your-api-key-here
YOUCAM_SECRET_KEY=your-secret-key-here
```

## Running the Server

```bash
# Development mode (with auto-reload)
source .venv/bin/activate
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Code Quality

### Linting
```bash
source .venv/bin/activate
ruff check app/
```

### Auto-fix linting issues
```bash
ruff check app/ --fix
```

### Format code
```bash
ruff format app/
```

### Check formatting
```bash
ruff format app/ --check
```

## Dependencies (Latest as of Dec 2024)

- `fastapi==0.115.6` - Web framework
- `uvicorn==0.34.0` - ASGI server
- `httpx==0.28.1` - Async HTTP client
- `pydantic==2.10.4` - Data validation
- `pydantic-settings==2.6.1` - Settings management
- `ruff==0.8.4` - Linter & formatter

## API Endpoints

- `GET /` - Root endpoint
- `POST /api/analyze` - Upload image and start analysis
- `GET /api/result/{task_id}` - Get analysis results
- `GET /api/health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Testing

```bash
# Manual testing via API docs
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/health
```
