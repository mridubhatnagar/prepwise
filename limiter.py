from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter instance imported by app.py (for registration) and by
# controllers (for @limiter.limit decorators).  Default key function is IP
# address; individual endpoints override this where needed.
limiter = Limiter(key_func=get_remote_address)
