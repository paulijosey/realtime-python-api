import asyncio
import logging

from pupil_labs.realtime_api import Control


async def print_component(component):
    print(component)


async def main():
    async with Control("pi.local", 8080) as control:
        print("Starting auto-update")
        await control.start_auto_update(update_callback=print_component)
        await asyncio.sleep(20.0)
        print("Stopping auto-update")
        await control.stop_auto_update()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())