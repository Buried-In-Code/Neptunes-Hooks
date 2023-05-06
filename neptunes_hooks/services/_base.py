__all__ = ["Service"]

import logging
from typing import Any, Dict

from ratelimit import limits, sleep_and_retry
from request import post
from requests.exceptions import ConnectionError, HTTPError, JSONDecodeError, ReadTimeout

from neptunes_hooks.service.exceptions import ServiceError

LOGGER = logging.getLogger(__name__)
MINUTE = 60


class Service:
    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Neptune's Hooks",
        }
        self.timeout = timeout

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _perform_post_json_request(
        self,
        params: Dict[str, str] = None,
        body: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        if params is None:
            params = {}
        if body is None:
            body = {}

        try:
            response = post(
                self.url,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
                json=body,
            )
            response.raise_for_status()
            return response.json()
        except ConnectionError as err:
            LOGGER.critical(err)
            raise ServiceError(f"Unable to connect to `{self.url}`") from err
        except HTTPError as err:
            LOGGER.error(err)
            raise ServiceError(err.response.text) from err
        except JSONDecodeError as err:
            LOGGER.critical(err)
            raise ServiceError(f"Unable to parse response from `{self.url}` as Json") from err
        except ReadTimeout as err:
            LOGGER.warning(err)
            raise ServiceError("Service took too long to respond") from err

    @sleep_and_retry
    @limits(calls=20, period=MINUTE)
    def _perform_post_data_request(
        self,
        params: Dict[str, str] = None,
        body: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        if params is None:
            params = {}
        if body is None:
            body = {}

        try:
            response = post(
                self.url,
                params=params,
                headers=self.headers,
                timeout=self.timeout,
                data=body,
            )
            response.raise_for_status()
            return response.json()
        except ConnectionError as err:
            LOGGER.critical(err)
            raise ServiceError(f"Unable to connect to `{self.url}`") from err
        except HTTPError as err:
            LOGGER.error(err)
            raise ServiceError(err.response.text) from err
        except JSONDecodeError as err:
            LOGGER.critical(err)
            raise ServiceError(f"Unable to parse response from `{self.url}` as Json") from err
        except ReadTimeout as err:
            LOGGER.warning(err)
            raise ServiceError("Service took too long to respond") from err
