"""Agent Routes — Invokes the LangGraph state machine and persists execution data."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from agent.api.auth_utils import get_current_user
from agent.api.database import get_db
from agent.api.models import ApprovalRequest, Chat, Message, User
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
    """Save user message, run agent workflow, and handle approval suspensions."""
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
        agent_result = agent_graph.invoke(
            initial_state,
            config={
                "run_name": f"Chat-{chat_id[:8]}",
                "tags": ["groq-llama-3", f"user:{user.username}"],
                "metadata": {
                    "chat_id": chat_id,
                    "user_id": user.id,
                },
            },
        )
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

    # 3. Check if suspended for Human-in-the-Loop review
    generated_code = agent_result.get("code", "")
    agent_status = agent_result.get("status", "")

    if agent_status == "awaiting_approval":
        # Create an approval record for the UI to query and authorize
        approval_req = ApprovalRequest(
            chat_id=chat.id,
            status="pending",
            reason=agent_result.get("approval_reason", "Dangerous or destructive action requested"),
            proposed_code=generated_code,
            checkpoint_state=dict(agent_result),
        )
        db.add(approval_req)
        db.commit()

    # 4. Generate AST flow graph (stored in JSONB column)
    flow_graph_dict = None
    if generated_code:
        try:
            flow_graph_dict = generate_flow_graph(generated_code)
        except Exception:
            flow_graph_dict = None

    # 5. Store assistant response with optimization metrics
    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=agent_result.get("final_output") or agent_result.get("error_summary") or "Execution completed.",
        code=generated_code,
        optimized_code=agent_result.get("optimized_code"),
        optimization_metrics=agent_result.get("optimization_metrics"),
        stdout=agent_result.get("stdout", ""),
        stderr=agent_result.get("stderr", ""),
        status=agent_status,
        tokens_used=agent_result.get("total_tokens", 0),
        cost_usd=agent_result.get("total_cost", 0.0),
        flow_graph=flow_graph_dict,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return MessageResponse.model_validate(assistant_msg)


@router.post("/chats/{chat_id}/approvals/{approval_id}", response_model=MessageResponse)
def resolve_approval(
    chat_id: str,
    approval_id: int,
    action: str,  # "approve" | "reject"
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resume or cancel execution for a suspended Human-in-the-Loop task."""
    chat = db.query(Chat).filter(Chat.chat_id == chat_id, Chat.owner_id == user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    approval = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.id == approval_id, ApprovalRequest.chat_id == chat.id)
        .first()
    )
    if not approval or approval.status != "pending":
        raise HTTPException(status_code=400, detail="Invalid or already resolved approval request.")

    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'.")

    approval.status = "approved" if action == "approve" else "rejected"
    db.commit()

    # Resume the workflow from the saved checkpoint state
    resumed_state = dict(approval.checkpoint_state)
    resumed_state["human_approved"] = action == "approve"
    resumed_state["status"] = "running" if action == "approve" else "rejected"

    try:
        agent_result = agent_graph.invoke(
            resumed_state,
            config={
                "run_name": f"Chat-{chat_id[:8]}-Resumed",
                "tags": ["groq-llama-3", f"user:{user.username}", "hitl-resumed"],
                "metadata": {"chat_id": chat_id, "user_id": user.id},
            },
        )
    except Exception as e:
        error_msg = Message(
            chat_id=chat.id,
            role="assistant",
            content=f"Workflow failed upon resume: {str(e)}",
            status="error",
        )
        db.add(error_msg)
        db.commit()
        db.refresh(error_msg)
        return MessageResponse.model_validate(error_msg)

    generated_code = agent_result.get("code", "")
    flow_graph_dict = None
    if generated_code:
        try:
            flow_graph_dict = generate_flow_graph(generated_code)
        except Exception:
            flow_graph_dict = None

    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=agent_result.get("final_output") or agent_result.get("error_summary") or "Resumed execution finished.",
        code=generated_code,
        optimized_code=agent_result.get("optimized_code"),
        optimization_metrics=agent_result.get("optimization_metrics"),
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
    """Generate an AST flow graph for arbitrary Python code without running an agent[cite: 18]."""
    try:
        return generate_flow_graph(data.code)
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Code syntax error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flow graph: {e}")