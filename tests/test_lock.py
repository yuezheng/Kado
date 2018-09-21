import asyncio
import unittest

from redis_lock.lock import Lock
from tests.utils import async_testcase


REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
}


class TestLock(unittest.TestCase):
    def setUp(self):
        pass

    @async_testcase
    async def test_lock_and_unlock(self):
        lock = Lock("lock_test", "primary", REDIS_CONFIG["host"], REDIS_CONFIG["port"])
        await lock.lock()
        self.assertEqual(lock.is_locked, True)
        await asyncio.sleep(15)
        self.assertEqual(lock.is_locked, True)
        await lock.unlock()
        self.assertEqual(lock.is_locked, False)


if __name__ == '__main__':
    unittest.main()
