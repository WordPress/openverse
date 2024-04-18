import uvicorn
from decouple import config


if __name__ == "__main__":
    is_local = config("ENVIRONMENT") == "local"
    port: int = config("PORT", default="8000", cast=int)

    uvicorn.run(
        "conf.asgi:application",
        host="0.0.0.0",
        port=port,
        workers=1,
        reload=is_local,
        # Reload directories are resolved relative to the current working
        # directory, which is the API project root set by ``Dockerfile``.
        reload_dirs=[
            ".",  # default, API directory
            "../py-packages/",
        ],
        log_level="debug",
        log_config={
            "version": 1,
            "formatters": {
                "generic": {
                    "format": "[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s",  # noqa: E501
                },
            },
        },
        access_log=False,
    )
