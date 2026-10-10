"""Human-in-the-Loop module — Approval gates for dangerous operations."""

from agent.hitl.approval import request_approval, check_if_approval_needed, ApprovalResult

__all__ = ["request_approval", "check_if_approval_needed", "ApprovalResult"]