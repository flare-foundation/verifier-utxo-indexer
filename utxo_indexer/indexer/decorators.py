import functools
import time


def retry(n: int, exception_type: tuple[type[Exception], ...] | type[Exception] = Exception):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            errors = []
            for _ in range(n):
                try:
                    return func(*args, **kwargs)
                except exception_type as e:
                    errors.append(e)
                    time.sleep(0.5)
            raise Exception(errors)

        return inner

    return decorator
