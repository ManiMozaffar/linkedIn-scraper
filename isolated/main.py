import json
import ast
import logging
import re

from aiohttp import web

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def is_safe_expression(node) -> bool:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return False
    if isinstance(node, ast.NameConstant) and isinstance(node.value, (
        bool, type(None)
    )):
        return True
    if isinstance(node, ast.Name):
        return node.id.isidentifier()
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        return all(is_safe_expression(value) for value in node.values)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return is_safe_expression(node.operand)
    if isinstance(node, ast.Compare):
        return (is_safe_expression(node.left) and
                all(
                    is_safe_expression(
                        comparator
                    ) for comparator in node.comparators
                ) and
                all(isinstance(op, (
                    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE
                )) for op in node.ops)
                )
    return False


def safe_eval(
        expression,
        context: list,
        filter: list,
        regex=r'\b(?!\band\b|\bor\b)\w+\b'
) -> dict:
    context_dict = {item: (item in filter) for item in context}

    try:
        try:
            ast_expression = ast.parse(expression, mode='eval')
            explaination = None
        except Exception as err:
            explaination = type(err).__name__
            raise err

        if not is_safe_expression(ast_expression.body):
            raise ValueError("Unsafe expression")
        compiled_expression = compile(ast_expression, '<string>', 'eval')
        evaluation = eval(compiled_expression, {}, context_dict)
        result = {
            "success": True,
            "evaluation": evaluation,
            "namespaces": list(set((re.findall(regex, expression))))
        }
        logging.info(result)
        return result
    except Exception as e:
        logging.error(f"Error: {e}")
        return {
            "success": False,
            "evaluation": None,
            "error": explaination or f"Invalid Expression -> {str(e)}",
        }


async def handle_post(request):
    """ An isolated request handler to handle boolean evaluation """
    try:
        data = await request.json()
        return web.json_response(
            safe_eval(data["expression"], data["context"], data["filter"]),
            status=200
        )
    except (json.JSONDecodeError or KeyError):
        return web.json_response(
            {
                "success": False,
                "evaluation": None,
                "error": "Invalid data"
            }, status=400
        )


app = web.Application()
app.router.add_post("/", handle_post)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=9999)
