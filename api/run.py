from decouple import config

import uvicorn


if __name__ == "__main__":
    # Default value matches ``conf/settings/base.py``.
    is_local = config("ENVIRONMENT", default="local") == "local"

    uvicorn.run(
        "conf.asgi:application",
        host="0.0.0.0",
        port=8000,
        workers=1,
        reload=is_local,
        log_level="debug",
        log_config={
            "version": 1,
            "formatters": {
                "generic": {
                    "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s",  # noqa: E501
                },
            },
        },
    )
