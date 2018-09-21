import asyncio
import logging

from asyncio.futures import CancelledError
from uuid import uuid1

import aioredis


_logger = logging.getLogger(__name__)


_redis_lock_lua_unlock_script = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("del",KEYS[1])
else
    return 0
end
"""


_redis_lock_lua_keepalive_script = """
if redis.call("get",KEYS[1]) == ARGV[1] then
    return redis.call("expire",KEYS[1],6)
else
    return 0
end
"""


class Lock(object):
    def __init__(self, service_name, lock_name, host, port, db=0, password=None):
        self._redis_config = {
            "host": host,
            "port": port,
            "db": db,
            "password": password,
        }

        self._name = f"{service_name}:lock:{lock_name}"
        self._value = None
        self._timeout = 10

    async def _get_redis_conn(self):
        config = self._redis_config
        pool = await aioredis.create_redis_pool((config["host"], config["port"]),
                                                db=config["db"],
                                                password=config["password"] or None,
                                                encoding="utf-8",
                                                maxsize=4096)
        return pool

    async def _keep_alive(self, value):
        while True:
            pool = await self._get_redis_conn()
            with await pool as conn:
                for _ in range(150):
                    try:
                        ack = await asyncio.wait_for(
                            conn.eval(_redis_lock_lua_keepalive_script, [self._name], [value]),
                            self._timeout / 2)
                    except CancelledError:
                        raise
                    except Exception:
                        _logger.warning("Exception occurs on keep alive process", exc_info=True)
                        conn.close()
                        await asyncio.sleep(0.1)
                        break
                    else:
                        if not ack:
                            # Lock losted
                            _logger.warning("Lock %r is lost during keep alive process", self._name)
                            return
                        await asyncio.sleep(2)

    async def lock(self):
        if self._value is not None:
            raise Exception("Already locked")
        self._value = uuid1().hex

        while True:
            pool = await self._get_redis_conn()
            with await pool as conn:
                try:
                    ack = await asyncio.wait_for(
                        conn.set(self._name, self._value,
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
                    self._keep_alive_task = asyncio.ensure_future(self._keep_alive(self._value))
                    return self._keep_alive_task

    async def unlock(self):
        if self._value is None:
            return

        try:
            ack = None
            self._keep_alive_task.cancel()

            async def _unlock_task():
                pool = await self._get_redis_conn()
                with await pool as conn:
                    try:
                        ack = await conn.eval(
                            _redis_lock_lua_unlock_script, [self._name], [self._value])
                    except Exception:
                        conn.close()
                        raise
                return ack

            ack = await asyncio.wait_for(_unlock_task(), 10)
        finally:
            self._value = None
            if ack is not None:
                _logger.debug(f"Unlock success of {self._name}, res: {ack}")
            else:
                _logger.warning(f"Failed unlock of {self._name}, res: {ack}")

    @property
    def is_locked(self):
        return self._value is not None
