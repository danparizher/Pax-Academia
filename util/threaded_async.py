import asyncio
from typing import TypeVar, ParamSpec, Callable, Awaitable
from concurrent.futures import ThreadPoolExecutor

T = TypeVar("T")
P = ParamSpec("P")

# decorator that takes a synchronous function and returns an asynchronous one
# It does this by creating a secondary thread and async busy waiting for it to complete
def make_async(sync_func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    async def async_func(*args: P.args, **kwargs: P.kwargs) -> T:
        with ThreadPoolExecutor() as executor:
            thread = executor.submit(
                sync_func,
                *args,
                **kwargs,
            )

            while thread.running():
                await asyncio.sleep(0.1)

            return thread.result()

    return async_func


__all__ = ["make_async"]

if __name__ == "__main__":
    import time

    async def original():
        print("before")
        time.sleep(1)
        print("after")

    async def run_original():
        await asyncio.gather(original(), original())

    print("original:")
    asyncio.run(run_original())
    """
    original:
    before
    after
    before
    after
    """

    @make_async
    def made_async():
        print("before")
        time.sleep(1)
        print("after")

    async def run_made_async():
        await asyncio.gather(made_async(), made_async())

    print("\nmade_async:")
    asyncio.run(run_made_async())
    """
    made_async:
    before
    before
    after
    after
    """
