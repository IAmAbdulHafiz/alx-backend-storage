#!/usr/bin/env python3
""" Implementing an expiring web cache and tracker """

from functools import wraps
import redis
import requests
from typing import Callable

redis_met = redis.Redis()


def count_requests(method: Callable) -> Callable:
    """ Decortator """
    @wraps(method)
    def wrapper(url):
        """ Wrapper for decorators """
        redis_met.incr(f"count:{url}")
        cached_html = redis_met.get(f"cached:{url}")
        if cached_html:
            return cached_html.decode('utf-8')
        html = method(url)
        redis_met.setex(f"cached:{url}", 10, html)
        return html

    return wrapper


@count_requests
def get_page(url: str) -> str:
    """ Obtain the HTML content of URL """
    reqs = requests.get(url)
    return reqs.text
