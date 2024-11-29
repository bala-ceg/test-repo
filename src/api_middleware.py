import logging
import uuid
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Middleware to check if the application is in maintenance mode
class MaintenanceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client):
        super().__init__(app)
        self.redis_client = redis_client
    async def dispatch(self, request, call_next):
        if request.url.path != "/online" and self.redis_client.get("settings:offline") == "True":
            logging.warning("Service Unavailable - Maintenance Mode")
            return JSONResponse(content={"detail": "Service Unavailable - Maintenance Mode"}, status_code=503)
        response = await call_next(request)
        return response

# Middleware to remove the Server header from responses
class RemoveServerHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Server"] = "My Assistant" #todo add container ID
        return response

# Middleware to generate a request ID for each request, and add it to the request
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        # Attach the request ID to the request's state
        request.state.id = request_id
        response = await call_next(request)
        # Optionally, add the request ID to the response headers
        response.headers['X-Request-ID'] = request_id
        return response