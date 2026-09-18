from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from app.models import MCQQuestionCreate, MCQQuestionResponse, QuestionListResponse
from app.database import get_questions_collection
from app.auth import get_current_user

router = APIRouter(prefix="/questions", tags=["MCQ Questions"])

def format_question_doc(doc: dict) -> MCQQuestionResponse:
    return MCQQuestionResponse(
        id=str(doc["_id"]),
        question=doc.get("question", ""),
        optionA=doc.get("optionA", ""),
        optionB=doc.get("optionB", ""),
        optionC=doc.get("optionC", ""),
        optionD=doc.get("optionD", ""),
        correctOption=doc.get("correctOption"),
        created_by=doc.get("created_by"),
        created_at=doc.get("created_at")
    )

@router.post(
    "",
    response_model=MCQQuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new MCQ question (Requires JWT Authentication)"
)
async def upload_question(
    question_in: MCQQuestionCreate,
    current_user: dict = Depends(get_current_user)
):
    questions_collection = get_questions_collection()
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "question": question_in.question.strip(),
        "optionA": question_in.optionA.strip(),
        "optionB": question_in.optionB.strip(),
        "optionC": question_in.optionC.strip(),
        "optionD": question_in.optionD.strip(),
        "correctOption": question_in.correctOption.upper().strip() if question_in.correctOption else None,
        "created_by": current_user["username"],
        "user_id": current_user["id"],
        "created_at": now_iso
    }

    result = await questions_collection.insert_one(doc)
    doc["_id"] = result.inserted_id

    return format_question_doc(doc)

@router.get(
    "",
    response_model=QuestionListResponse,
    summary="Get list of all uploaded MCQ questions"
)
async def get_questions_list(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    questions_collection = get_questions_collection()
    query = {}
    if search:
        query["question"] = {"$regex": search, "$options": "i"}

    cursor = questions_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    total = await questions_collection.count_documents(query)

    question_list = [format_question_doc(doc) for doc in documents]

    return QuestionListResponse(
        total=total,
        questions=question_list
    )

@router.get(
    "/{question_id}",
    response_model=MCQQuestionResponse,
    summary="Get a single MCQ question by ID"
)
async def get_question_by_id(question_id: str):
    questions_collection = get_questions_collection()

    doc = None
    if ObjectId.is_valid(question_id):
        doc = await questions_collection.find_one({"_id": ObjectId(question_id)})

    if not doc:
        # Fallback to string matching if saved as string
        doc = await questions_collection.find_one({"_id": question_id})

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID '{question_id}' not found."
        )

    return format_question_doc(doc)
