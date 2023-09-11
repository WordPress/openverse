import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "conf.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "local",
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
