import asyncio

loop = asyncio.get_event_loop()


def async_testcase(coro):
    def wrapper(*args, **kwargs):
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper