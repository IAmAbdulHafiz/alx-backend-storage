#!/usr/bin/env python3
"""
Redis module, Writing strings to Redis
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    def count_calls(method: Caallable) -> Callable:
    Returns a Callable
    """
    @wraps(method)
    def wrapper(self, *args, **kwds):
        """
        def wrapper(self, *args, **kwds):
        Returns wrapper
        """
        key_met = method.__qualname__
        self._redis.incr(key_met)
        return method(self, *args, **kwds)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    def call_history(method: Callable) -> Callable:
    Returns a Callable
    """
    @wraps(method)
    def wrapper(self, *args, **kwds):
        """
        def wrapper(self, *args, **kwds):
        Returns wrapper
        """
        key_met = method.__qualname__
        inpt_met = key_met + ':inputs'
        outp_met = key_met + ":outputs"
        data = str(args)
        self._redis.rpush(inpt_met, data)
        fins = method(self, *args, **kwds)
        self._redis.rpush(outp_met, str(fins))
        return fins
    return wrapper


def replay(func: Callable):
    """
    def replay(func: Callable):
    Displays history of calls of a particular function
    """
    r = redis.Redis()
    key_met = func.__qualname__
    inpt_met = r.lrange("{}:inputs".format(key_met), 0, -1)
    outp_met = r.lrange("{}:outputs".format(key_met), 0, -1)
    calls_number = len(inpt_met)
    times_str = 'times'
    if calls_number == 1:
        times_str = 'time'
    fins = '{} was called {} {}:'.format(key_met, calls_number, times_str)
    print(fins)
    for y, v in zip(inpt_met, outp_met):
        fins = '{}(*{}) -> {}'.format(
            key_met, y.decode('utf-8'), v.decode('utf-8'))
        print(fins)


class Cache():
    """
    Store instance of Redis client as private variable _redis
    Flush the instance using flushdb
    """
    def __init__(self):
        """
        def __init__(self):
        Store instance of Redis client as private variable _redis
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store history of inputs and outputs for a particular function
        """
        gens = str(uuid.uuid4())
        self._redis.set(gens, data)
        return gens

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """
        Convert data back to desired format
        """
        value = self._redis.get(key)
        return value if not fn else fn(value)

    def get_int(self, key):
        return self.get(key, int)

    def get_str(self, key):
        value = self._redis.get(key)
        return value.decode("utf-8")
