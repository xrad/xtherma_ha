"""
REST API client for Xtherma Fernportal cloud integration
"""

import asyncio
import aiohttp
import datetime

from .const import LOGGER

class RateLimitError(Exception):
    def __init__(self):
        super().__init__("API is busy")

class GeneralError(Exception):
    def __init__(self, code: int):
        super().__init__("General error")
        self.code = code

class TimeoutError(Exception):
    def __init__(self):
        super().__init__("timeout")

class XthermaClient:
    def __init__(self, url: str, api_key: str, serial_number: str, session: aiohttp.ClientSession):
        self._url = f"{url}/{serial_number}"
        self._api_key = api_key
        self._session = session

    def _now(self) -> int:
        return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

    async def async_get_data(self):
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            # return test_data
            async with self._session.get(self._url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except aiohttp.ClientResponseError as err:
            LOGGER.debug("API error: %s", err)
            if err.status == 429:   
                raise RateLimitError()
            raise GeneralError(err.status)
        except asyncio.TimeoutError:
            LOGGER.error("API request timed out")
            raise TimeoutError()
        except Exception as err:
            LOGGER.error("Unknown API error: %s", err)
            return None

async def test():
    from const import (
        FERNPORTAL_URL, KEY_SETTINGS, KEY_TELEMETRY,
        KEY_ENTRY_NAME, KEY_ENTRY_UNIT, KEY_ENTRY_VALUE, KEY_ENTRY_INPUT_FACTOR,
    )
    import os
    api_key = os.environ['API_KEY']
    serial_number = os.environ['SERIAL_NUMBER']
    print("creating client session")
    session = aiohttp.ClientSession()
    print("creating instance")
    inst = XthermaClient(url=FERNPORTAL_URL, api_key=api_key, serial_number=serial_number, session=session)
    print("request data")
    done = False
    while not done:
        try:
            raw = await inst.async_get_data()
            done = True
        except RateLimitError as err:
            print("Rate limiting, wait...")
            await asyncio.sleep(10)
        except Exception as err:
            print(f"Unknown error {err}")
    print(raw)
    print("------------- top-level:")
    for key in raw:
        print(f"{key}")
    print("------------- settings:")
    for i,e in enumerate(raw[KEY_SETTINGS]):
        print(f"{i} - {e[KEY_ENTRY_NAME]} = {e[KEY_ENTRY_VALUE]} unit {e[KEY_ENTRY_UNIT]} input {e[KEY_ENTRY_INPUT_FACTOR]}")
    print("------------- telemetry:")
    for i,e in enumerate(raw[KEY_TELEMETRY]):
        print(f"{i} - {e[KEY_ENTRY_NAME]} = {e[KEY_ENTRY_VALUE]} unit {e[KEY_ENTRY_UNIT]} input {e[KEY_ENTRY_INPUT_FACTOR]}")
    await session.close()

if __name__ == "__main__":
    asyncio.run(test())
