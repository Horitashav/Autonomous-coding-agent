"""AST Security Checker — Scans code for dangerous patterns without executing it."""

import ast
from dataclasses import dataclass, field
from agent.config import FORBIDDEN_MODULES


class SecurityViolation(Exception):
    """Raised when code contains a security violation."""

    def __init__(self, message: str, violations: list[str]):
        self.violations = violations
        super().__init__(message)


@dataclass
class ASTCheckResult:
    """Result of an AST security scan."""

    is_safe: bool
    violations: list[str] = field(default_factory=list)
    node_count: int = 0


# Built-in functions that should never be executed dynamically
FORBIDDEN_BUILTINS: set[str] = {
    "eval",        # Executes arbitrary string code
    "exec",        # Executes arbitrary Python statements
    "compile",     # Compiles raw strings into executable code objects
    "__import__",  # Bypasses standard import statements
    "globals",     # Accesses global symbol table (can extract __builtins__)
    "breakpoint",  # Drops into interactive debugger (freezes the process)
    "exit",        # Prematurely halts the interpreter
    "quit",        # Prematurely halts the interpreter
    "input",       # Waits for user keyboard input (hangs indefinitely)
}


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor that checks for security violations."""

    def __init__(self, forbidden_modules: set[str] | None = None):
        self.forbidden_modules = forbidden_modules or FORBIDDEN_MODULES
        self.violations: list[str] = []
        self.node_count: int = 0

    def visit(self, node: ast.AST):
        """Track the total number of nodes visited."""
        self.node_count += 1
        return super().visit(node)

    def visit_Import(self, node: ast.Import):
        """Catches standard imports like 'import os' or 'import os as safe_os'."""
        for alias in node.names:
            top_level = alias.name.split(".")[0]
            if top_level in self.forbidden_modules:
                self.violations.append(
                    f"Forbidden import: '{alias.name}' (line {node.lineno}). "
                    f"The module '{top_level}' is blocked for security."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Catches 'from os import system' or 'from subprocess import run'."""
        if node.module:
            top_level = node.module.split(".")[0]
            if top_level in self.forbidden_modules:
                imported_names = ", ".join(alias.name for alias in node.names)
                self.violations.append(
                    f"Forbidden import: 'from {node.module} import {imported_names}' "
                    f"(line {node.lineno}). The module '{top_level}' is blocked for security."
                )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Catches function calls like eval(...) or __import__(...)."""
        func_name = None

        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name and func_name in FORBIDDEN_BUILTINS:
            self.violations.append(
                f"Forbidden function call: '{func_name}()' (line {node.lineno}). "
                f"This function is blocked for security."
            )

        self.generic_visit(node)


def check_code_safety(code: str) -> ASTCheckResult:
    """Scan Python code for security violations without executing it."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return ASTCheckResult(
            is_safe=False,
            violations=[f"Code has a syntax error: {e}"],
            node_count=0,
        )

    visitor = SecurityVisitor()
    visitor.visit(tree)

    return ASTCheckResult(
        is_safe=len(visitor.violations) == 0,
        violations=visitor.violations,
        node_count=visitor.node_count,
    )