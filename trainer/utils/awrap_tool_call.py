import inspect

from langchain.agents.middleware.types import AgentMiddleware


class AwrapToolCall(AgentMiddleware):
    def __init__(self, guard_fun):
        self._guard_fun = guard_fun

    def wrap_tool_call(self, request, handler):
        return self._guard_fun(request, handler)

    async def awrap_tool_call(self, request, handler):

        if inspect.iscoroutinefunction(self._guard_fun):
            res = await self._guard_fun(request, handler)
        else:
            res = self._guard_fun(request, handler)

        if inspect.isawaitable(res):
            return await res
        return res
