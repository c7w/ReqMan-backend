from rest_framework.throttling import SimpleRateThrottle


# class GeneralThrottle(SimpleRateThrottle):
#     def __init__(self):
#         """
#         intentionally not calling super().__init__()
#         """
#         pass
#
#     def get_ident(self, request):
#         xff = request.META.get('HTTP_X_FORWARDED_FOR')
#         if not xff:
#             return None
#         xff = xff.split(',')
#         return xff[0].strip()
#
#     def define_type(self, t: str):
#         self.scope = t
#         self.rate = self.get_rate()
#         self.num_requests, self.duration = self.parse_rate(self.rate)
#
#     def allow_request(self, request, view):
#         ident = self.get_ident(request)
#         print(dir(request))
#         if not ident:
#             return True
#
#         if not request.user:
#             self.define_type("visitor")
#             self.ident = ident
#         else:
#             self.define_type("user")
#             self.ident = ident
#
#         assert self.rate is not None
#
#         self.key = self.cache_format % {"scope": self.scope, "ident": self.ident}
#
#         self.history = self.cache.get(self.key, [])
#         self.now = self.timer()
#
#         # Drop any requests from the history which have now passed the
#         # throttle duration
#         while self.history and self.history[-1] <= self.now - self.duration:
#             self.history.pop()
#         if len(self.history) >= self.num_requests:
#             return self.throttle_failure()
#         return self.throttle_success()
