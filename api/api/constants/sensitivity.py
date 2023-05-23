"""
Sensitivity tokens denoting what made a given result "sensitive".

``PROVIDER_SUPPLIED`` is currently unused because we do not actually
ingest sensitive content from providers (knowingly). It is included
here to cover the gamut of potential use-cases and to provide an
opportunity to document it as an exceptional case.
"""

TEXT = "sensitive_text"
PROVIDER_SUPPLIED = "provider_supplied_sensitivity"
USER_REPORTED = "user_reported_sensitivity"
