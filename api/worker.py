import asyncio

from uvicorn.workers import UvicornWorker as BaseUvicornWorker


# Django does not support Lifespan Protocol
# https://asgi.readthedocs.io/en/latest/specs/lifespan.html
# https://github.com/django/django/pull/13636
# https://code.djangoproject.com/ticket/31508
# Using uvicorn.workers.UvicornWorker throws INFO warning:
#   "ASGI 'lifespan' protocol appears unsupported."
# To avoid that we need to disable 'lifespan' in the worker
class UvicornWorker(BaseUvicornWorker):
    async def _serve(self):
        loop = asyncio.get_running_loop()
        loop.set_debug(True)
        return await super()._serve()

    # CONFIG_KWARGS = {"lifespan": "off"}
