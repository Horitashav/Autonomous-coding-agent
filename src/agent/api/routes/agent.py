"""Agent Routes — Invokes the LangGraph state machine and persists execution data."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.api.auth_utils import get_current_user
from agent.api.database import get_db
from agent.api.models import Chat, Message, User
from agent.api.schemas import FlowGraphRequest, MessageCreate, MessageResponse
from agent.orchestrator.graph import agent_graph
from agent.visualization.flow_analyzer import generate_flow_graph

router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
def send_message(
    chat_id: str,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save user message, run agent workflow, and save response with AST JSONB."""
    chat = (
        db.query(Chat)
        .filter(Chat.chat_id == chat_id, Chat.owner_id == user.id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    # 1. Store user prompt
    user_msg = Message(
        chat_id=chat.id,
        role="user",
        content=data.content,
    )
    db.add(user_msg)
    chat.updated_at = datetime.now(timezone.utc)
    db.commit()

    # 2. Invoke LangGraph state machine
    initial_state = {
        "prompt": data.content,
    }
    if data.project_path:
        initial_state["project_path"] = data.project_path

    try:
        agent_result = agent_graph.invoke(initial_state)
    except Exception as e:
        error_msg = Message(
            chat_id=chat.id,
            role="assistant",
            content=f"Agent workflow encountered an error: {str(e)}",
            status="error",
        )
        db.add(error_msg)
        db.commit()
        db.refresh(error_msg)
        return MessageResponse.model_validate(error_msg)

    # 3. Generate AST flow graph (stored in JSONB column)
    flow_graph_dict = None
    generated_code = agent_result.get("code", "")
    if generated_code:
        try:
            flow_graph_dict = generate_flow_graph(generated_code)
        except Exception:
            flow_graph_dict = None

    # 4. Store assistant response
    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=agent_result.get("final_output") or agent_result.get("error_summary") or "Execution completed.",
        code=generated_code,
        stdout=agent_result.get("stdout", ""),
        stderr=agent_result.get("stderr", ""),
        status=agent_result.get("status", ""),
        tokens_used=agent_result.get("total_tokens", 0),
        cost_usd=agent_result.get("total_cost", 0.0),
        flow_graph=flow_graph_dict,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return MessageResponse.model_validate(assistant_msg)


@router.post("/flow-graph")
def create_flow_graph(data: FlowGraphRequest):
    """Generate an AST flow graph for arbitrary Python code without running an agent."""
    try:
        return generate_flow_graph(data.code)
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Code syntax error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flow graph: {e}")