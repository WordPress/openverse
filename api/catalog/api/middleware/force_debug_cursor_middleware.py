from django.db import connection


# Makes DB query logging possible when debugging is disabled
# by forcing the connection to use a debug cursor.
#
# WARNING: This can have performance implications and
# should only be used in production temporarily.
class ForceDebugCursorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.before(request)
        response = self.get_response(request)
        self.after(request)
        return response

    def before(self, request):
        connection.force_debug_cursor = True

    def after(self, request):
        pass
