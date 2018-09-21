import asyncio


if __name__ == '__main__':
    import unittest
    import test as it

    try:
        loop = asyncio.get_event_loop()
        unittest.main(None, argv=["test", "discover", "-v", "-s", it.__path__[0]])
    finally:
        loop.close()