# API Rules

**API-specific patterns and rules**

Last Updated: 2026-01-21

---

## API Architecture

### Framework
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Key Directories
- `api/routes/` - API endpoints
- `api/services/` - Business logic
- `api/models/` - Data models

---

## Endpoint Patterns

### Basic Endpoint

```python
from fastapi import APIRouter, HTTPException
from api.models.request import RequestModel
from api.services.service import Service

router = APIRouter()

@router.post("/endpoint")
async def endpoint(request: RequestModel):
    try:
        result = service.process(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### ETL Endpoint Pattern

```python
@router.post("/etl/run")
async def run_etl(request: ETLRequest):
    try:
        job_id = etl_service.start_etl(request)
        return {"job_id": job_id, "status": "started"}
    except Exception as e:
        logger.error(f"ETL error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Error Handling

### Error Response Pattern

```python
from fastapi import HTTPException

try:
    result = process_request(request)
    return result
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Request/Response Models

### Pydantic Models

```python
from pydantic import BaseModel

class ETLRequest(BaseModel):
    games: list[str]
    wipe: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "games": ["game1", "game2"],
                "wipe": False
            }
        }

class ETLResponse(BaseModel):
    job_id: str
    status: str
    message: str
```

---

## Performance Requirements

### Response Time
- **Target:** < 200ms per endpoint
- **Optimization:** Use async operations
- **Caching:** Cache when appropriate

### Background Tasks
- Use FastAPI background tasks for long operations
- Return job ID immediately
- Provide status endpoint

---

## Authentication

### API Key Pattern (Future)

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != valid_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## Logging

### Logging Pattern

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/endpoint")
async def endpoint(request: RequestModel):
    logger.info(f"Processing request: {request}")
    try:
        result = process(request)
        logger.info(f"Request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise
```

---

## Related Rules

- `core.md` - Core rules (error handling, code standards)
- `etl.md` - ETL service patterns
- `testing.md` - API testing requirements

---

*Last Updated: 2026-01-15*
