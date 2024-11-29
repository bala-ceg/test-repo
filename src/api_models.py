from typing import Annotated, List
from pydantic import BaseModel, Field, field_validator
from fastapi import FastAPI, Query
from uuid import UUID

""" Status Check Response """
class StatusCheckResponse(BaseModel):
    status: str
    
    @field_validator('status')
    def check_status(cls, v):
        if v not in ["healthy", "unhealthy"]:
            raise ValueError('status must be "healthy" or "unhealthy"')
        return v

""" Command Execute Request and Response """
class CommandExecuteRequest(BaseModel):
    command: Annotated[str, Query(max_length=160)]

class CommandExecuteResponse(BaseModel):
    id: UUID
    tk: Annotated[str, Query(max_length=32)]
    request: str
    response: str

""" Undo Command Execute Request and Response """
class UndoCommandExecuteRequest(BaseModel):
    id: UUID

class UndoCommandExecuteResponse(BaseModel):
    id: UUID

""" Command List Response """
class CommandListResponse(BaseModel):
    commands: List[str]

class RatingSetRequest(BaseModel):
    t_id: UUID
    rating: int