import asyncio
import logging

from redis_lock.lock import Lock


logger = logging.getLogger(__name__)


REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
}


async def main():
    lock = Lock("lock_test", "primary", REDIS_CONFIG["host"], REDIS_CONFIG["port"])
    await lock.lock()
    print(lock.is_locked)
    await asyncio.sleep(15)
    print(lock.is_locked)
    await lock.unlock()
    print(lock.is_locked)


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    finally:
        loop.close()
