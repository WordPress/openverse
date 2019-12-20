from rest_framework import status
from rest_framework.response import Response


def input_error_response(errors):
    fields = [f for f in errors]
    messages = ''
    for field in errors:
        error = errors[field]
        for e in error:
            messages += e + ' '

    # Don't return "non field errors" in deprecation exceptions. There is no
    # other way to recover the affected fields other than parsing the error.
    if fields == ['non_field_errors']:
        split_error = messages.split(' ')
        field_idx = messages.index('Parameter') + 1
        fields = [split_error[field_idx].replace("'", '')]

    return Response(
        status=status.HTTP_400_BAD_REQUEST,
        data={
            'error': 'InputError',
            'detail': f'Invalid input given for field(s) {fields}.'
                      f' Hint: {messages}',
            'fields': fields
        }
    )
