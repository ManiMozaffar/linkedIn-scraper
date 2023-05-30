import logging
from typing import Callable, List, Any
import inspect
import traceback

from core.abc import AbstractEngine


class BaseTaskEngine(AbstractEngine):
    base_url = "http://127.0.0.1:8000"

    def __init__(self):
        self.register_tasks()

    @property
    def tasks(self) -> List[Callable]:
        """Gets all tasks starting with task_"""
        return [
            getattr(self, method_name) for _, method_name in self._tasks
        ]

    def register_tasks(self):
        self._tasks = []
        for attr in dir(self):
            func = getattr(self, attr)
            if hasattr(func, '_task_info'):
                level = func._task_info['level']
                self._tasks.append((level, attr))
        self._tasks.sort()

    async def setup(self) -> dict:
        """Overide this method to configure setup for the crawler

        Returns: dependancies for all tasks
        """
    async def tear_down(self) -> Any:
        """Overide this method to teardown setup for the crawler"""

    def get_task_kwargs(
        self, task: Callable, setup_data: dict
    ) -> dict:
        signature = inspect.signature(task)
        default_values = {
            param.name: param.default
            for param in signature.parameters.values()
            if param.default is not inspect.Parameter.empty
        }
        return {**default_values, **setup_data}

    async def execute(self) -> Any:
        for _, task_name in self._tasks:
            task = getattr(self, task_name)
            try:
                setup_data = await self.setup()
            except Exception as error:
                logging.error(
                    f"\n error raised for task: {task.__name__}: {error}"
                    f"\n traceback: {traceback.format_exc()} \n"
                )
                break

            try:
                kwargs = self.get_task_kwargs(task, setup_data)
                await task(
                    **kwargs
                )
            except Exception as error:
                logging.error(
                    f"\n error raised for task: {task.__name__}: {error}"
                    f"\n traceback: {traceback.format_exc()} \n"
                )
            finally:
                try:
                    await self.tear_down(**setup_data)
                except Exception as error:
                    logging.error(
                        f"\n error raised for teardown: {error} \n"
                        f"\n traceback: {traceback.format_exc()} \n"
                    )
