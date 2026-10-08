"""Flow Analyzer — Converts Python AST into a visual flow graph for React Flow."""

import ast
from typing import Any


def generate_flow_graph(code: str) -> dict[str, list]:
    """Parse Python code and generate a flow graph structure.

    Args:
        code: Python source code string

    Returns:
        Dict with "nodes", "edges", and "summary" lists

    Raises:
        SyntaxError: If the code cannot be parsed
    """
    tree = ast.parse(code)
    analyzer = FlowGraphBuilder()
    analyzer.visit(tree)
    return {
        "nodes": analyzer.nodes,
        "edges": analyzer.edges,
        "summary": analyzer.summary,
    }


class FlowGraphBuilder(ast.NodeVisitor):
    """AST visitor that builds node-edge flow graph data from Python code."""

    def __init__(self):
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.summary: list[dict[str, Any]] = []
        self._id_counter = 0
        self._y_position = 0
        self._x_position = 0
        self._parent_stack: list[str] = []

    def _next_id(self) -> str:
        self._id_counter += 1
        return str(self._id_counter)

    def _add_node(
        self,
        node_type: str,
        label: str,
        line: int = 0,
        details: str = "",
    ) -> str:
        """Add a graph node and connect it to its immediate parent."""
        node_id = self._next_id()
        self._y_position += 80

        type_colors = {
            "module": "#075E46",        # Root module
            "function": "#059669",      # Green
            "class": "#2563EB",         # Blue
            "condition": "#D97706",     # Amber
            "loop": "#EA580C",          # Orange
            "error_handler": "#DC2626",  # Red
            "return": "#6B7280",        # Gray
            "call": "#7C3AED",          # Purple
            "assignment": "#64748B",    # Slate
        }

        self.nodes.append({
            "id": node_id,
            "type": "default",
            "data": {
                "label": label,
                "nodeType": node_type,
                "line": line,
                "details": details,
                "color": type_colors.get(node_type, "#6B7280"),
            },
            "position": {"x": self._x_position, "y": self._y_position},
            "style": {
                "background": type_colors.get(node_type, "#6B7280"),
                "color": "#FFFFFF",
                "border": "none",
                "borderRadius": "8px",
                "padding": "10px 16px",
                "fontSize": "13px",
                "fontWeight": "500",
                "minWidth": "150px",
                "textAlign": "center",
            },
        })

        indent = "  " * len(self._parent_stack)
        self.summary.append({
            "id": node_id,
            "type": node_type,
            "label": label,
            "line": line,
            "depth": len(self._parent_stack),
            "display": f"{indent}{'├── ' if self._parent_stack else ''}{label}",
        })

        if self._parent_stack:
            parent_id = self._parent_stack[-1]
            self.edges.append({
                "id": f"e{parent_id}-{node_id}",
                "source": parent_id,
                "target": node_id,
                "type": "smoothstep",
                "animated": node_type == "loop",
                "style": {"stroke": "#94A3B8"},
            })

        return node_id

    def visit_Module(self, node: ast.Module):
        root_id = self._add_node("module", "Module", line=1)
        self._parent_stack.append(root_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = ", ".join(a.arg for a in node.args.args)
        label = f"def {node.name}({args})"
        node_id = self._add_node(
            "function", label, line=node.lineno, details=f"Function with {len(node.body)} statements"
        )
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        args = ", ".join(a.arg for a in node.args.args)
        label = f"async def {node.name}({args})"
        node_id = self._add_node("function", label, line=node.lineno)
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef):
        bases = ", ".join(getattr(b, "id", getattr(b, "attr", "?")) for b in node.bases)
        label = f"class {node.name}" + (f"({bases})" if bases else "")
        node_id = self._add_node(
            "class", label, line=node.lineno, details=f"Class with {len(node.body)} members"
        )
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_If(self, node: ast.If):
        test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        if len(test_str) > 40:
            test_str = test_str[:37] + "..."
        label = f"if {test_str}"
        node_id = self._add_node("condition", label, line=node.lineno)

        self._parent_stack.append(node_id)
        for child in node.body:
            self.visit(child)
        if node.orelse:
            else_id = self._add_node(
                "condition", "else", line=node.orelse[0].lineno if node.orelse else node.lineno
            )
            self._parent_stack.append(else_id)
            for child in node.orelse:
                self.visit(child)
            self._parent_stack.pop()
        self._parent_stack.pop()

    def visit_For(self, node: ast.For):
        target = ast.unparse(node.target) if hasattr(ast, "unparse") else "item"
        iter_str = ast.unparse(node.iter) if hasattr(ast, "unparse") else "iterable"
        if len(iter_str) > 30:
            iter_str = iter_str[:27] + "..."
        label = f"for {target} in {iter_str}"
        node_id = self._add_node("loop", label, line=node.lineno)
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_While(self, node: ast.While):
        test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        label = f"while {test_str}"
        node_id = self._add_node("loop", label, line=node.lineno)
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_Try(self, node: ast.Try):
        node_id = self._add_node("error_handler", "try / except", line=node.lineno)
        self._parent_stack.append(node_id)
        self.generic_visit(node)
        self._parent_stack.pop()

    def visit_Return(self, node: ast.Return):
        val = ""
        if node.value:
            val = ast.unparse(node.value) if hasattr(ast, "unparse") else "value"
            if len(val) > 30:
                val = val[:27] + "..."
        label = f"return {val}" if val else "return"
        self._add_node("return", label, line=node.lineno)