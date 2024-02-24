# !/usr/bin/env python

"""
This module is responsible for creating the FastAPI application
and performing startup and shutdown actions.
"""

from fastapi import FastAPI

from lifecycle import lifespan

app = FastAPI(title="Message Processor App", version="1.0", lifespan=lifespan)


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(startup_db())
#     try:
#         loop.run_until_complete(listen_to_kafka())
#     except KeyboardInterrupt:
#         pass
#     finally:
#         loop.run_until_complete(shutdown_db())
