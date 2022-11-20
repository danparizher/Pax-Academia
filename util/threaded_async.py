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

    @make_async
    def test():
        print("before")
        time.sleep(1)
        print("after")

    async def main():
        await asyncio.gather(test(), test())

    asyncio.run(main())
    # output:
    """
    before
    before
    after
    after
    """
