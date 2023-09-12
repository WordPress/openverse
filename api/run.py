import os

import uvicorn


if __name__ == "__main__":
    is_local = os.getenv("ENVIRONMENT") == "local"

    app = "conf.asgi:static_files_application" if is_local else "conf.asgi:application"

    uvicorn.run(
        app,
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
