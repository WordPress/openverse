from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


def get_status_code_view(data, status_code=200):
    """
    Get a class-based that returns the given data and status code on all HTTP
    methods. Useful for blanket discontinuation of API endpoints.

    :param data: the dictionary to serialize as the JSON response
    :param status_code: the status code of the returned response
    :return: the class based view that returns the same response for all methods
    """

    @method_decorator(csrf_exempt, name='dispatch')
    class StatusCodeView(View):
        status = status_code

        def dispatch(self, request, *args, **kwargs):
            return JsonResponse(
                status=self.status,
                data=data,
            )

    return StatusCodeView
