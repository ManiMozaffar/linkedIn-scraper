import ast


def is_safe_expression(node):
    if isinstance(node, ast.NameConstant) and isinstance(node.value, bool):
        return True
    if isinstance(node, ast.Name):
        return node.id.isidentifier()
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        return all(is_safe_expression(value) for value in node.values)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return is_safe_expression(node.operand)
    if isinstance(node, ast.Compare):
        return (is_safe_expression(node.left) and
                all(is_safe_expression(comparator) for comparator in node.comparators) and
                all(isinstance(op, (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE))
                    for op in node.ops))
    return False


def safe_eval(expression, context):
    try:
        ast_expression = ast.parse(expression, mode='eval')
        if not is_safe_expression(ast_expression.body):
            raise ValueError("Unsafe expression")
        compiled_expression = compile(ast_expression, '<string>', 'eval')
        return eval(compiled_expression, {}, context)
    except Exception as e:
        print(f"Error: {e}")
        return None


var1 = True
var2 = False
context = {'var1': var1, 'var2': var2}
expression = "(var1 or var2) and (var1) and var1 and ((var1))"

result = safe_eval(expression, context)
print(result)
