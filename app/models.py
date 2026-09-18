from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- User Auth Models ---
class UserSignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Full name of the user", examples=["John Doe"])
    username: str = Field(..., min_length=3, max_length=30, description="Unique username", examples=["johndoe"])
    password: str = Field(..., min_length=6, max_length=100, description="Password (min 6 characters)", examples=["secret123"])

class UserLoginRequest(BaseModel):
    username: str = Field(..., description="Username", examples=["johndoe"])
    password: str = Field(..., description="User password", examples=["secret123"])

class UserResponse(BaseModel):
    id: str
    name: str
    username: str
    created_at: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- MCQ Question Models ---
class MCQQuestionCreate(BaseModel):
    question: str = Field(..., min_length=3, description="The MCQ question statement", examples=["What is the capital of France?"])
    optionA: str = Field(..., description="Option A", examples=["London"])
    optionB: str = Field(..., description="Option B", examples=["Paris"])
    optionC: str = Field(..., description="Option C", examples=["Berlin"])
    optionD: str = Field(..., description="Option D", examples=["Madrid"])
    correctOption: Optional[str] = Field(None, description="Optional correct option (A, B, C, or D)", examples=["B"])

class MCQQuestionResponse(BaseModel):
    id: str
    question: str
    optionA: str
    optionB: str
    optionC: str
    optionD: str
    correctOption: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None

class QuestionListResponse(BaseModel):
    total: int
    questions: List[MCQQuestionResponse]
