import logging
from json.decoder import JSONDecodeError
from typing import Dict, Any

from requests import post
from requests.exceptions import ConnectionError, HTTPError

LOGGER = logging.getLogger(__name__)
BASE_URL = 'https://np.ironhelmet.com'
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Neptune\'s Hooks'
}


def pull_data(game_id: int, api_code: str) -> Dict[str, Any]:
    try:
        response = post(url=f"{BASE_URL}/api", headers=HEADERS, data={
            'api_version': '0.1',
            'game_number': game_id,
            'code': api_code
        })
        if response.status_code == 200:
            LOGGER.debug(f"{response.status_code}: POST - {response.url}")
            try:
                data = response.json()['scanning_data']
                return data
            except (JSONDecodeError, KeyError):
                LOGGER.critical(f'Unable to parse the response message: {response.text}')
        else:
            LOGGER.error(f"{response.status_code}: POST - {response.url} - {response.text}")
    except (ConnectionError, HTTPError):
        LOGGER.error(f"Unable to access: `{BASE_URL}/api`")
    return {}
