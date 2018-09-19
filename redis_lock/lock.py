import asyncio
from uuid import uuid1

import aioredis


_redlock_lua_unlock_script = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""


class Lock(object):
    def __init__(self, host, port, db, password, channel, service_name, lock_name):
        self._redis_config = {
            "host": host,
            "port": port,
            "db": db,
            "password": password,
            "channel": channel
        }

        self._name = f"{service_name}:lock:{lock_name}"
        self._value = None
        self._timeout = 10

    async def _get_redis_conn(self):
        config = self._redis_config
        pool = await aioredis.create_pool((config["host"], config["port"]),
                                          db=config["db"],
                                          password=config["password"] or None,
                                          encoding="utf-8",
                                          maxsize=4096)
        return pool

    async def lock(self):
        if self._value is not None:
            raise Exception("Already locked")
        self._value = uuid1().hex

        while True:
            with await self._get_redis_conn() as conn:
                try:
                    ack = await asyncio.wait_for(conn.set(self._name, self._value,
                                                          expire=self._timeout,
                                                          exist=conn.SET_IF_NOT_EXIST),
                                                 5)
                except asyncio.TimeoutError:
                    ack = None
                    conn.close()
                if not ack:
                    # Lock exist, wait it release
                    await asyncio.sleep(2)
                else:
                    # Lock acquired
                    return

    async def unlock(self):
        if self._value is None:
            return

        try:
            async def _unlock_task():
                with await self._get_redis_conn() as conn:
                    try:
                        ack = await conn.eval(_redlock_lua_unlock_script, [self._name], [self._value])
                    except Exception:
                        conn.close()
                        raise
                return ack

            await asyncio.wait_for(_unlock_task(), 10)
        finally:
            self._value = None
