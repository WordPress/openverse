import os

import uvicorn


if __name__ == "__main__":
    is_local = os.getenv("ENVIRONMENT") == "local"

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
        access_log=False,
    )
