from functools import wraps

from aiohttp.web_exceptions import HTTPUnauthorized


def login_required(f):
    @wraps(f)
    async def decorated_function(method, *args, **kwargs):
        if method.request.admin:
            return await f(method, *args, **kwargs)
        else:
            raise HTTPUnauthorized
    return decorated_function
