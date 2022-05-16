import re
import io

camel_to_snake_pattern = re.compile("(.)([A-Z][a-z]+)")
camel_to_snake_pattern2 = re.compile("([a-z0-9])([A-Z])")


def camel_to_snake(name):
    # name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    name = camel_to_snake_pattern.sub(r"\1_\2", name)
    return camel_to_snake_pattern2.sub(r"\1_\2", name).lower()


def iterable_to_stream(
    iterable, buffer_size=io.DEFAULT_BUFFER_SIZE
) -> io.BufferedReader:
    """
    Lets you use an iterable (e.g. a generator) that yields bytestrings as a read-only
    input stream.

    The stream implements Python 3's newer I/O API (available in Python 2's io module).
    For efficiency, the stream is buffered.
    """

    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                length = len(b)  # We're supposed to return at most this much
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:length], chunk[length:]
                b[: len(output)] = output
                return len(output)
            except StopIteration:
                return 0  # indicate EOF

    return io.BufferedReader(IterStream(), buffer_size=buffer_size)


class RequiredParameterCheck(object):
    """A decorator that checks if at least on named parameter is present"""

    MODE_OR = 0
    MODE_AND = 1

    def __init__(self, required, mode=MODE_OR):
        self.required = sorted(required)
        self.mode = mode

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            found_paramater = sorted([req for req in self.required if req in kwargs])
            if self.mode == self.MODE_OR and found_paramater:
                return func(*args, **kwargs)
            elif self.mode == self.MODE_AND and found_paramater == self.required:
                return func(*args, **kwargs)
            else:
                raise ValueError(
                    f"Required parameter `{', '.join(self.required)}` is missing."
                )

        wrapper.__name__ = func.__name__
        wrapper.__dict__.update(func.__dict__)
        wrapper.__doc__ = func.__doc__
        return wrapper
