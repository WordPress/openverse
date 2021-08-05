from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import filter_none, force_real_str


class CustomAutoSchema(SwaggerAutoSchema):

    def get_operation(self, operation_keys=None):
        operation_keys = operation_keys or self.operation_keys

        consumes = self.get_consumes()
        produces = self.get_produces()

        body = self.get_request_body_parameters(consumes)
        query = self.get_query_parameters()
        parameters = body + query
        parameters = filter_none(parameters)
        parameters = self.add_manual_parameters(parameters)

        operation_id = self.get_operation_id(operation_keys)
        summary, description = self.get_summary_and_description()
        security = self.get_security()
        assert security is None or isinstance(security, list), \
            "security must be a list of security requirement objects"
        deprecated = self.is_deprecated()
        tags = self.get_tags(operation_keys)

        responses = self.get_responses()

        return openapi.Operation(
            operation_id=operation_id,
            description=force_real_str(description),
            summary=force_real_str(summary),
            responses=responses,
            parameters=parameters,
            consumes=consumes,
            produces=produces,
            tags=tags,
            security=security,
            deprecated=deprecated,
            **{'x-code-samples': self.overrides.get('code_examples')}
        )
