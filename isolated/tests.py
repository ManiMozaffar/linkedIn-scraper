import unittest
from main import safe_eval


class TestSafeEval(unittest.TestCase):
    def test_safe_eval_security(self):
        unsafe_expressions = [
            "import os",
            "os.system('ls')",
            "exec('print(\"Hello, World!\")')",
            "__import__('os').system('ls')",
            "getattr(__builtins__, 'exec')('print(\"Hello, World!\")')",
            "globals()",
            "locals()",
        ]

        context = ["holland", "germany", "iceland"]
        filter = ["iceland"]

        for expression in unsafe_expressions:
            result = safe_eval(expression, context, filter)
            self.assertIn(result.get("error"),  [
                "Invalid Expression", "Syntax Error"
            ])

    def test_example_safe_eval(self):
        context = ["holland", "germany", "iceland"]
        filter = ["iceland"]
        result = safe_eval("iceland and germany", context, filter)
        self.assertEqual(result["evaluation"], False)

        result = safe_eval(
            "(iceland and germany) or germany", context, filter
        )
        self.assertEqual(result["evaluation"], False)

        result = safe_eval(
            "((iceland or holland) and (germany or iceland))",
            context, filter
        )
        self.assertEqual(result["evaluation"], True)


if __name__ == '__main__':
    unittest.main()
