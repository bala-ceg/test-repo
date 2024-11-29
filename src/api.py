import logging
import jwt
import json
import redis
from hashlib import md5
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.cors import CORSMiddleware
from openai import OpenAI
from contextlib import asynccontextmanager
# Local imports
from src.api_models import StatusCheckResponse, CommandExecuteRequest, CommandExecuteResponse, RatingSetRequest, UndoCommandExecuteResponse
from src.assistant.assistant import screen_request, toolset, evaluate_screen_request, process_request, UnsupportedCategoryError
from src import config
from src.api_middleware import MaintenanceMiddleware, RemoveServerHeaderMiddleware, RequestIDMiddleware
import hashlib

# Simplify logging setup
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenAI client setup
client = OpenAI(api_key=config.OPENAI_API_KEY,base_url=config.OPENAI_BASE_URL)

print(config.OPENAI_API_KEY)

# Redis client setup
redis_client = redis.Redis(**config.REDIS_CONFIG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis_client.ping()
        logging.info("Connected to Redis")
        yield
        redis_client.close()
    except redis.RedisError as e:
        logging.error(f"Redis connection error: {e}")

app = FastAPI(title="My Assistant", lifespan=lifespan)

# Setup middleware
app.add_middleware(RemoveServerHeaderMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(MaintenanceMiddleware, redis_client=redis_client)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for JWT token verification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



async def verify_jwt(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        print(payload)
        return payload.get("sub")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

# Define the endpoints
@app.get("/", include_in_schema=False)
async def root():
    return {"name": "My Assistant", "documentation": "/docs"}

# Health check endpoints
@app.get("/health-check/server", include_in_schema=False)
async def server_health_status():
    return StatusCheckResponse(status="healthy")

@app.get("/health-check/datastore", include_in_schema=False)
async def datastore_health_status():
    try:
        if redis_client.ping():
            return StatusCheckResponse(status="healthy")
        else:
            raise HTTPException(status_code=500)
    except redis.RedisError as e:
        logging.error(f"Redis check error: {e}")
        raise HTTPException(status_code=500)

@app.get("/health-check/model", include_in_schema=False)
async def model_health_status():
    try:
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages= [{"role" : "system", "content" : "reply with 'healthy'"},{"role" : "user", "content" : "SYN"}],
            temperature=0.0)
        
        if not resp.choices[0].message or resp.choices[0].message.content != "healthy":
            raise HTTPException(status_code=500)

        response = resp.choices[0].message
        print(response)
        return StatusCheckResponse(status=response.content)
    except Exception as e:
        logging.error(f"Model check error: {e}")
        raise HTTPException(status_code=500)


# User endpoints
@app.post("/command/execute")
async def execute_command(req: CommandExecuteRequest, request: Request, store_id: str = Depends(verify_jwt), user_agent: str = Header(None), authorization: str = Header(None)):  

    # For unhandled request categories, missing tools
    generic_rejection = "Sorry, I can't help with that. Please contact support."

    try:
        request_id = request.state.id

        logging.warning(req.model_dump())
        redis_client.set(request_id, json.dumps(req.model_dump()))
        jwt_token = authorization.split(" ")[1] if authorization else ""
        #logging.info(f"Toolset available: {toolset}")

        if req.command:
            screen_resp = screen_request(req.command, toolset)

            tool_definition, tool_name = evaluate_screen_request(
                toolset=toolset, 
                screen_resp=screen_resp, 
                supported_categories=['modification','file system interaction']
            )

            resp = {
                "tool_definition": tool_definition,
                "tool_name": tool_name
            }

            logging.info(f"Response: {resp}")
            logging.info(resp)

            resp = process_request(
                request=req.command, 
                toolset={'definitions': tool_definition, 'tools' : [tool_name]},
                tool_config={
                    'store_id': store_id,
                    'authorization_header': "Bearer " + jwt_token,
                    'endpoint': config.BASE_URL,
                }
            )

            # md5 tool_name
            tk = hashlib.md5(tool_name.encode()).hexdigest()

            redis_client.lpush('requests', json.dumps({
            'request_id': request_id,
            'store_id': store_id,
            'status': "Success",
            'tk': tk,
            'command': req.command,
            'response':json.dumps(resp[0])
            }))
            return CommandExecuteResponse(id=request_id, status="Success", tk=tk, request=req.command, response=json.dumps(resp[0]))
        else:
            raise HTTPException(status_code=500, detail="No command provided")
    except Exception as e:
        logging.error(f"Error executing command: {req.command}", exc_info=True)

        if isinstance(e, UnsupportedCategoryError):
            return CommandExecuteResponse(id=request_id, status="Error", tk='', request=req.command, response=generic_rejection)

        raise HTTPException(status_code=500, detail="Error executing command")

@app.get("/command/{command_id}/undo")
async def undo_command(command_id: str):
    try:
        # Get the previous state of the command from Redis
        command_data = redis_client.get(command_id)
        if command_data is not None:
            command_data = json.loads(command_data)
            previous_state = command_data.get('state')
            if previous_state is not None:
                # Restore the previous state of the command
                command_data['state'] = previous_state
                redis_client.set(command_id, json.dumps(command_data))
                return UndoCommandExecuteResponse(id=command_id)
            else:
                return {'statusCode': 404, 'command_id': command_id, 'response': f"Previous state not found"}
        else:
            return {'statusCode': 404, 'command_id': command_id, 'response': f"Command not found"}
    except Exception as e:
        logging.error(f"Error undoing command: {command_id}", exc_info=True)
        return {'statusCode': 400, 'command_id': command_id, 'response': f"Error undoing command"}


@app.post("/command/set-rating")
async def set_rating(req: RatingSetRequest, store_id: str = Depends(verify_jwt)):
    try:
        # Storing rating in Redis with request ID as key
        redis_client.set(f"rating:{req. t_id}", req.rating)

        return {"message": "Rating for request ID set successfully"}
    except Exception as e:
        logging.error(f"Error setting rating for request ID", exc_info=True)
        raise HTTPException(status_code=500, detail="Error setting rating")

# Live update capabilities
@app.post("/offline")
async def offline(store_id: str = Depends(verify_jwt)):
    print(store_id)
    try:
        redis_client.set("settings:offline", "True")
        return {"status": "Success"}
    except redis.RedisError as e:
        logging.error(f"Redis error during offline mode: {e}")
        return HTTPException(status_code=500, detail="Error setting offline mode")

@app.post("/online")
async def online(store_id: str = Depends(verify_jwt)):
    print(store_id)
    try:
        redis_client.set("settings:offline", "False")
        return {"status": "Success"}
    except redis.RedisError as e:
        logging.error(f"Redis error during online mode: {e}")
        return HTTPException(status_code=500, detail="Error setting online mode")

@app.post("/screen_system_instruction")
async def screen_system_instruction(instruction: str, store_id: str = Depends(verify_jwt)):
    try:
        redis_client.set("settings:screen_system_instruction", instruction)
        return {"status": "Success"}
    except redis.RedisError as e:
        logging.error(f"Redis error during screen system instruction: {e}")
        return HTTPException(status_code=500, detail="Error setting screen system instruction")


