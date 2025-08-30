import ast
import operator as op

def get_expression_value(expression: str) -> str:

    def _eval_node(node):
        #Supported operators
        OPERATORS = {
            ast.Add: op.add,
            ast.Sub: op.sub,
            ast.Mult: op.mul,
            ast.Div: op.truediv,
            ast.Pow: op.pow,
            ast.BitXor: op.xor,
            ast.USub: op.neg,
            ast.Mod: op.mod,
            ast.FloorDiv: op.floordiv,
            ast.UAdd: op.pos,
        }
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise TypeError(f"Unsupported constant type: {type(node.value).__name__}")
        elif isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            operator = OPERATORS.get(type(node.op))
            if operator is None:
                raise TypeError(f"Unsupported binary operator: {type(node.op).__name__}")
            
            return operator(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval_node(node.operand)
            operator = OPERATORS.get(type(node.op))
            if operator is None:
                raise TypeError(f"Unsupported binary operator: {type(node.op).__name__}")
            return operator(operand)
        else:
            raise TypeError(f"Unsupported expression: {type(node).__name__}")
            
    node = ast.parse(expression, mode='eval')
    result = _eval_node(node.body)
    result = round(result, 2) #Round to 2 demical places
    return f"{result: .2f}"

print (get_expression_value("9.896 - 4.012 + (-13.23456908) - (- 2**(-1.05))"))  # Output
