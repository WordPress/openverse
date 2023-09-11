"""
Openverse asynchronous entrypoint compatibility tools.

While existing asyncio tools make it easy to associate and track resources
according to a particular event loop, it is not possible to monitor the
closure of the event loop and ensure that resources associated with it are
cleanly disposed of before the closure. While `weakref.finalize` would be an
intuitive tool to use here, because those resources keep references to the
event loop, so long as they are open, there are still referents to the loop,
causing it to never get garbage collected.

Which raises the other issue: without managing the per-event-loop resources
in this explicit way, we would inevitably introduce a memory leak without
some method of cleaning those resources periodically.

Therefore, the easiest and least complex way to do it, is to wrap asgiref's
`async_to_sync` helper function with Openverse specific functionality that
opens and closes resources that our async entrypoints rely on. This allows
us to write async code as though everything were running inside a single
event loop (which will only be the case once the application is ASGI-ified)
without introducing a memory leak or local complexity to those functions.

Before we're able to get to run the full application under ASGI, this wrapped
version of `async_to_sync` will also need to handle other async clients like
Redis and Elasticsearch (if needed).
"""

from asgiref.sync import async_to_sync as base_async_to_sync

from api.utils.httpx import get_httpx_client


def async_to_sync(
    awaitable: callable = None,
    *,
    force_new_loop: bool = False,
    httpx: bool = True,
):
    """
    Wrap and async function to make it callable from a sync context.

    Key-word arguments allow configuration of the resources in the
    context or are passed to ``asgiref.sync.async_to_sync`` when relevant.
    """
    if awaitable is None:
        return lambda f: async_to_sync(
            awaitable=f,
            force_new_loop=force_new_loop,
            httpx=httpx,
        )

    async def wrapped(*args, **kwargs):
        httpx_client = await get_httpx_client() if httpx else None

        try:
            return await awaitable(*args, **kwargs)
        finally:
            if httpx_client is not None:
                await httpx_client.aclose()

    return base_async_to_sync(wrapped, force_new_loop=force_new_loop)
