from rest_framework.throttling import SimpleRateThrottle

class GeneralThrottle(SimpleRateThrottle):
    def __init__(self):
        """
        intentionally not calling super().__init__()
        """
        pass

    def define_type(self, t: str):
        self.scope = t
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)

    def allow_request(self, request, view):
        if not request.user:
            self.define_type('visitor')
            self.ident = self.get_ident(request)
        else:
            self.define_type('user')
            self.ident = str(request.user.id)

        assert self.rate is not None

        self.key = self.cache_format % {
            'scope': self.scope,
            'ident': self.ident
        }

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Drop any requests from the history which have now passed the
        # throttle duration
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()
        return self.throttle_success()


def SpecialThrottle(scope_name: str):
    class SpecialThrottleClass(SimpleRateThrottle):
        scope = scope_name

        def get_cache_key(self, request, view):
            return self.cache_format % {
                'scope': self.scope,
                'ident': self.get_ident(request)
            }
    return SpecialThrottleClass
