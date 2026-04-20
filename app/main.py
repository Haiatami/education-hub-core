# education-hub-core/app/main.py
import asyncio
import sys

from app.core.application import Application


async def main_async():
    app = Application()
    await app.run()


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
