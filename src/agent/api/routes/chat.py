"""Chat Routes — CRUD operations on user chat threads."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from agent.api.auth_utils import get_current_user
from agent.api.database import get_db
from agent.api.models import Chat, Message, User
from agent.api.schemas import ChatCreate, ChatDetail, ChatRename, ChatSummary, MessageResponse

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.get("/", response_model=list[ChatSummary])
def list_chats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch all chat threads belonging to the current user."""
    chats = db.query(Chat).filter(Chat.owner_id == user.id).order_by(Chat.updated_at.desc()).all()

    results = []
    for chat in chats:
        msg_count = (
            db.query(func.count(Message.id)).filter(Message.chat_id == chat.id).scalar() or 0
        )
        results.append(
            ChatSummary(
                id=chat.id,
                chat_id=chat.chat_id,
                name=chat.name,
                created_at=chat.created_at,
                updated_at=chat.updated_at,
                message_count=msg_count,
            )
        )
    return results


@router.post("/", response_model=ChatSummary, status_code=status.HTTP_201_CREATED)
def create_chat(
    data: ChatCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat thread."""
    chat = Chat(name=data.name, owner_id=user.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    return ChatSummary(
        id=chat.id,
        chat_id=chat.chat_id,
        name=chat.name,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        message_count=0,
    )


@router.get("/{chat_id}", response_model=ChatDetail)
def get_chat(
    chat_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve a complete chat session with full message history."""
    chat = db.query(Chat).filter(Chat.chat_id == chat_id, Chat.owner_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    return ChatDetail(
        id=chat.id,
        chat_id=chat.chat_id,
        name=chat.name,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[MessageResponse.model_validate(m) for m in chat.messages],
    )


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a chat and cascade-delete its messages."""
    chat = db.query(Chat).filter(Chat.chat_id == chat_id, Chat.owner_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    db.delete(chat)
    db.commit()


@router.put("/{chat_id}/rename", response_model=ChatSummary)
def rename_chat(
    chat_id: str,
    data: ChatRename,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rename a chat thread."""
    chat = db.query(Chat).filter(Chat.chat_id == chat_id, Chat.owner_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    chat.name = data.name
    db.commit()
    db.refresh(chat)

    msg_count = db.query(func.count(Message.id)).filter(Message.chat_id == chat.id).scalar() or 0
    return ChatSummary(
        id=chat.id,
        chat_id=chat.chat_id,
        name=chat.name,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        message_count=msg_count,
    )
