from django.db import connection


# Makes DB query logging possible when debugging is disabled
# by forcing the connection to use a debug cursor.
#
# WARNING: This can have performance implications and
# should only be used in production temporarily.
def force_debug_cursor_middleware(get_response):
    def middleware(request):
        connection.force_debug_cursor = True
        return get_response(request)

    return middleware
