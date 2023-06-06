from conf.settings.base import ENVIRONMENT


def export_environment(request):
    """Export the environment to the template context."""
    return {"ENVIRONMENT": ENVIRONMENT}
