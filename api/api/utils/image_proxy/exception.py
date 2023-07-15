from rest_framework import status
from rest_framework.exceptions import APIException


class UpstreamThumbnailException(APIException):
    status_code = status.HTTP_424_FAILED_DEPENDENCY
    default_detail = "Could not render thumbnail due to upstream provider error."
    default_code = "upstream_photon_failure"
