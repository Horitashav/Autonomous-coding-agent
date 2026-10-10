"""Flow Analyzer — Converts Python AST into a visual flow graph."""

import ast


def generate_flow_graph(code: str) -> dict[str, list]:
    """Parse Python code and generate a flow graph structure."""
    tree = ast.parse(code)
    analyzer = FlowGraphBuilder()
    analyzer.visit(tree)
    return {
        "nodes": analyzer.nodes,
        "edges": analyzer.edges,
        "summary": analyzer.summary,
    }


class FlowGraphBuilder(ast.NodeVisitor):
    def __init__(self):
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.summary: list[dict] = []
        self._id_counter = 0
        self._y_position = 0
        self._x_position = 250
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
        node_id = self._next_id()
        self._y_position += 90

        type_colors = {
            "module": "#075E46",
            "function": "#059669",
            "class": "#2563EB",
            "condition": "#D97706",
            "loop": "#EA580C",
            "error_handler": "#DC2626",
            "return": "#6B7280",
            "call": "#871658",  # Deep Berry for execution calls
            "assignment": "#4D123B",  # Dark Berry for assignments
            "import": "#1E293B",  # Slate for imports
        }

        self.nodes.append(
            {
                "id": node_id,
                "type": "default",
                "data": {
                    "label": label,
                    "nodeType": node_type,
                    "line": line,
                    "details": details,
                },
                "position": {"x": self._x_position, "y": self._y_position},
                "style": {
                    "background": type_colors.get(node_type, "#6B7280"),
                    "color": "#FAF6F0",
                    "border": "1px solid rgba(255,255,255,0.15)",
                    "borderRadius": "10px",
                    "padding": "10px 18px",
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "minWidth": "160px",
                    "textAlign": "center",
                },
            }
        )

        indent = "  " * len(self._parent_stack)
        self.summary.append(
            {
                "id": node_id,
                "type": node_type,
                "label": label,
                "line": line,
                "depth": len(self._parent_stack),
                "display": f"{indent}{'├── ' if self._parent_stack else ''}{label}",
            }
        )

        if self._parent_stack:
            parent_id = self._parent_stack[-1]
            self.edges.append(
                {
                    "id": f"e{parent_id}-{node_id}",
                    "source": parent_id,
                    "target": node_id,
                    "type": "smoothstep",
                    "animated": node_type in ("loop", "call"),
                    "style": {"stroke": "#871658", "strokeWidth": 2},
                }
            )

        return node_id

    def visit_Module(self, node: ast.Module):
        root_id = self._add_node("module", "Module Entry", line=1)
        self._parent_stack.append(root_id)
        for stmt in node.body:
            self.visit(stmt)
        self._parent_stack.pop()

    def visit_Import(self, node: ast.Import):
        names = ", ".join(alias.name for alias in node.names)
        self._add_node("import", f"import {names}", line=node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        names = ", ".join(alias.name for alias in node.names)
        self._add_node("import", f"from {mod} import {names}", line=node.lineno)

    def visit_Assign(self, node: ast.Assign):
        targets = [ast.unparse(t) for t in node.targets if hasattr(ast, "unparse")]
        label = f"{', '.join(targets)} = ..." if targets else "assign"
        self._add_node("assignment", label, line=node.lineno)

    def visit_Expr(self, node: ast.Expr):
        """Catches standalone expressions like print(...) calls."""
        if isinstance(node.value, ast.Call):
            call_name = ast.unparse(node.value.func) if hasattr(ast, "unparse") else "call()"
            if len(call_name) > 25:
                call_name = call_name[:22] + "..."
            self._add_node("call", f"call: {call_name}()", line=node.lineno)
        else:
            self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        args = ", ".join(a.arg for a in node.args.args)
        label = f"def {node.name}({args})"
        node_id = self._add_node("function", label, line=node.lineno)
        self._parent_stack.append(node_id)
        for stmt in node.body:
            self.visit(stmt)
        self._parent_stack.pop()

    def visit_If(self, node: ast.If):
        test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        if len(test_str) > 30:
            test_str = test_str[:27] + "..."
        node_id = self._add_node("condition", f"if {test_str}", line=node.lineno)
        self._parent_stack.append(node_id)
        for child in node.body:
            self.visit(child)
        if node.orelse:
            else_id = self._add_node("condition", "else", line=node.orelse[0].lineno)
            self._parent_stack.append(else_id)
            for child in node.orelse:
                self.visit(child)
            self._parent_stack.pop()
        self._parent_stack.pop()

    def visit_For(self, node: ast.For):
        target = ast.unparse(node.target) if hasattr(ast, "unparse") else "item"
        iter_str = ast.unparse(node.iter) if hasattr(ast, "unparse") else "iterable"
        if len(iter_str) > 20:
            iter_str = iter_str[:17] + "..."
        node_id = self._add_node("loop", f"for {target} in {iter_str}", line=node.lineno)
        self._parent_stack.append(node_id)
        for child in node.body:
            self.visit(child)
        self._parent_stack.pop()

    def visit_While(self, node: ast.While):
        test_str = ast.unparse(node.test) if hasattr(ast, "unparse") else "condition"
        node_id = self._add_node("loop", f"while {test_str}", line=node.lineno)
        self._parent_stack.append(node_id)
        for child in node.body:
            self.visit(child)
        self._parent_stack.pop()

    def visit_Return(self, node: ast.Return):
        val = ast.unparse(node.value) if node.value and hasattr(ast, "unparse") else ""
        if len(val) > 20:
            val = val[:17] + "..."
        self._add_node("return", f"return {val}".strip(), line=node.lineno)
